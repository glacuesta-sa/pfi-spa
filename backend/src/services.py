import json
import os
import random
import tempfile
import time

from flask import jsonify, request
from rdflib import Graph
import utils
import constants
import repository
import openai
import joblib


def set_llm_fields(disease):
    """
    Set on-the-fly generated fields by querying an LLM (Language Model). 
    Title, description, and causes fields for a given disease dictionary.

    Parameters:
    disease (dict): A dictionary containing information about the disease. The 'name' key must be present.

    This function constructs a prompt to query the OpenAI API to traverse the MONDO disease ontology and 
    retrieve the title, description, and causes of the disease. The retrieved information is then added 
    to the input dictionary.

    The format of the prompt ensures that the response is in JSON format, with specific fields: title, 
    description, and causes.

    Raises:
    KeyError: If 'name' is not present in the disease dictionary.
    """
    text = "This is the name of a disease in MONDO disease ontology: " + disease['name']
    text = text + ". Please traverse the ontology and get a title, description and causes of the disease. Do not include any additional text as the output, it has to have the following format, in JSON. Exclude json decorations, only keep json structure: title: title of the disease, description: brief description of the disease, causes: List of brief causes."
           
     # Initialize the OpenAI client with your API key
    client = None
    apiKey = os.getenv('OPENAI_API_KEY', '')
    if len(apiKey) > 0: 
        client = openai.OpenAI(api_key=apiKey)
        completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Mondo Ontology traverse assistant."},
            {"role": "user", "content": text}
        ])

        result_content = completion.choices[0].message.content

        # Convertir result_content de cadena JSON a diccionario de Python
        result_json = json.loads(result_content)

        disease['description'] = result_json['description']
        disease['title'] = result_json['title']
        disease['causes'] = result_json['causes']

def predict_relationship(disease_id, relationship_type, relationship_property):
    """
    Predict the target ID for a given disease ID, relationship type, and relationship property
    using a pre-trained Random Forest model stored in MongoDB.

    Parameters:
    disease_id (str): The identifier for the disease.
    relationship_type (str): The type of the relationship.
    relationship_property (str): The property of the relationship.

    Returns:
    str: The predicted target ID for the given inputs.
    """

    # wait if necessary
    for filename in constants.RANDOM_FOREST_MODEL_FILES:
        repository.wait_for_file_in_mongo(filename)

    best_rf = load_json_from_mongo('best_rf.pkl')
    le_disease = load_json_from_mongo('le_disease.pkl')
    le_relationship_type = load_json_from_mongo('le_relationship_type.pkl')
    le_relationship_property = load_json_from_mongo('le_relationship_property.pkl')
    le_target_id = load_json_from_mongo('le_target_id.pkl')
    le_disease_rel_prop = load_json_from_mongo('le_disease_rel_prop.pkl')

    # encode inputs
    disease_id_encoded = le_disease.transform([disease_id])[0]
    relationship_type_encoded = le_relationship_type.transform([relationship_type])[0]
    relationship_property_encoded = le_relationship_property.transform([relationship_property])[0]

    # feature engineering transcode of the filters
    disease_rel_prop = f"{disease_id_encoded}_{relationship_property_encoded}"

    # not seen labels handling
    if disease_rel_prop not in le_disease_rel_prop.classes_:
        disease_rel_prop_encoded = -1
    else:
        disease_rel_prop_encoded = le_disease_rel_prop.transform([disease_rel_prop])[0]

    # predict
    target_encoded = best_rf.predict([[disease_id_encoded, relationship_type_encoded, relationship_property_encoded, disease_rel_prop_encoded]])
    le_target_id.inverse_transform(target_encoded)

    # posible targets
    possible_targets = [t for t in le_target_id.classes_ if is_valid_relationship(relationship_property, t)]

    # randomize to not be deterministic
    predicted_target = random.choice(possible_targets)

    # TODO add relationship to data_model
    #set_llm_fields2

    return predicted_target

def is_valid_relationship(property_id, target_id):
    """
    Check if the relationship between a given property ID and target ID is valid based on the 
    predefined types of relationships.

    Parameters:
    property_id (str): The identifier for the property (relationship type).
    target_id (str): The identifier for the target entity.

    Returns:
    bool: True if the relationship is valid, False otherwise.
    """

    relationships_types = repository.get_data_model()['relationships_types']
    if property_id in relationships_types:
        if relationships_types[property_id] == constants.UBERON_STR and constants.UBERON_STR not in target_id:
            return False
        if relationships_types[property_id] == constants.HP_STR and constants.HP_STR not in target_id:
            return False
    return True

def get_hierarchy_by_mondo_id(mondo_id):

    """
    Generate a hierarchical representation of diseases starting from a given MONDO ID.

    This function retrieves the hierarchy of diseases starting from a specified MONDO ID
    and represents it in a format suitable for visualization. It builds a tree structure
    where each node represents a disease and its relationship to its parent.

    Parameters:
    mondo_id (str): The MONDO ID of the root disease to start the hierarchy from.

    Returns:
    list: A list of lists representing the hierarchy. Each sublist contains information
          about a disease node in the format [id, childLabel, parent, size, {"role": "style"}, "link"].

    The function performs the following steps:
    1. Fetches all diseases from the MongoDB collection and constructs a dictionary for quick lookup.
    2. Initializes the hierarchy list with the headers.
    3. Defines helper functions to add nodes to the hierarchy and to process the hierarchy recursively.
    4. Builds the hierarchy starting from the given MONDO ID.
    """

    diseases = list(repository.DISEASES_COLLECTION.find({}, {'_id': 0}))
    disease_dict = {d['id']: d for d in diseases}
    hierarchy = [["id", "childLabel", "parent", "size", {"role": "style"}, "link"]]
    id_map = {}
    current_id = 0

    def add_to_hierarchy(disease_id, parent_id, label, size, color):
        nonlocal current_id
        id_map[disease_id] = current_id
        hierarchy.append([current_id, label, parent_id, size, color, disease_id])
        current_id += 1

    def process_hierarchy(disease_id, parent_id):
        disease = disease_dict[disease_id]
        add_to_hierarchy(disease_id, parent_id, disease['name'], 1, "#1d8bf8")
        for child_id in disease.get('children', []):
            process_hierarchy(child_id, id_map[disease_id])

    if mondo_id in disease_dict:
        add_to_hierarchy(mondo_id, -1, disease_dict[mondo_id]['name'], 1, "#1d8bf8")
        for child_id in disease_dict[mondo_id].get('children', []):
            process_hierarchy(child_id, id_map[mondo_id])

    return hierarchy

def get_diseases_by_phenotypes(phenotype_ids):
    """
    Retrieve all diseases associated with all of the given phenotypes, excluding the specified phenotypes from the phenotypes list.

    :param phenotype_ids: A list of phenotype IDs (HP IDs).

    :return: A list of diseases associated with all the given phenotypes.
    """
    if not phenotype_ids:
        return []

    print(f"Filtering diseases by phenotypes: {phenotype_ids}")

    data_model = repository.get_data_model()

    # Get the initial set of disease IDs that contain the first phenotype
    initial_phenotype_id = phenotype_ids[0]
    initial_disease_ids = set(data_model['phenotype_to_diseases'].get(initial_phenotype_id, []))

    print(f"Initial disease IDs: {initial_disease_ids}")

    # Intersect with disease IDs that contain each of the other phenotypes
    for phenotype_id in phenotype_ids[1:]:
        current_disease_ids = set(data_model['phenotype_to_diseases'].get(phenotype_id, []))
        initial_disease_ids.intersection_update(current_disease_ids)
        print(f"Disease IDs after intersecting with {phenotype_id}: {initial_disease_ids}")

    # Retrieve the diseases that match all phenotypes
    diseases = [disease for disease in data_model['diseases'] if disease['id'] in initial_disease_ids]

    print(f"Matching diseases: {diseases}")

    # Exclude the specified HP relationships from the phenotypes list
    for disease in diseases:
        disease['phenotypes'] = [phenotype for phenotype in disease['phenotypes'] if phenotype['target'] not in phenotype_ids]

    return diseases

def get_diseases_by_age_onsets(age_onset_ids):
    """
    Retrieve all diseases associated with any of the given age onsets, excluding the specified age onsets from the age_onsets list.

    :param age_onset_ids: A list of age onset IDs (HP IDs).
    :param data_model: The data model containing diseases and their relationships.
    :return: A list of diseases associated with the given age onsets.
    """
    if not age_onset_ids:
        return []

    data_model = repository.get_data_model()

    # Get the initial set of disease IDs that contain the first age onset
    initial_age_onset_id = age_onset_ids[0]
    initial_disease_ids = set(data_model['age_onset_to_diseases'].get(initial_age_onset_id, []))

    # Intersect with disease IDs that contain each of the other age onsets
    for age_onset_id in age_onset_ids[1:]:
        current_disease_ids = set(data_model['age_onset_to_diseases'].get(age_onset_id, []))
        initial_disease_ids.intersection_update(current_disease_ids)

    # Retrieve the diseases that match all age onsets
    diseases = [disease for disease in data_model['diseases'] if disease['id'] in initial_disease_ids]

    # Exclude the specified age onsets from the age_onsets list
    for disease in diseases:
        disease['age_onsets'] = [age_onset for age_onset in disease['age_onsets'] if age_onset['target'] not in age_onset_ids]

    return diseases

def get_diseases_by_anatomical_structures(anatomical_ids):
    """
    Retrieve all diseases associated with any of the given anatomical structures, excluding the specified anatomical structures from the anatomical_structures list.

    :param anatomical_ids: A list of anatomical structure IDs (UBERON IDs).
    :param data_model: The data model containing diseases and their relationships.
    :return: A list of diseases associated with the given anatomical structures.
    """
    if not anatomical_ids:
        return []
    
    data_model = repository.get_data_model()

    # Get the initial set of disease IDs that contain the first anatomical structure
    initial_anatomical_id = anatomical_ids[0]
    initial_disease_ids = set(data_model['anatomical_to_diseases'].get(initial_anatomical_id, []))

    # Intersect with disease IDs that contain each of the other anatomical structures
    for anatomical_id in anatomical_ids[1:]:
        current_disease_ids = set(data_model['anatomical_to_diseases'].get(anatomical_id, []))
        initial_disease_ids.intersection_update(current_disease_ids)

    # Retrieve the diseases that match all anatomical structures
    diseases = [disease for disease in data_model['diseases'] if disease['id'] in initial_disease_ids]

    # Exclude the specified anatomical structures from the anatomical_structures list
    for disease in diseases:
        disease['anatomical_structures'] = [anatomical for anatomical in disease['anatomical_structures'] if anatomical['target'] not in anatomical_ids]

    return diseases

def get_diseases_by_filters(phenotype_ids, anatomical_ids, age_onset_ids):
    if not (phenotype_ids or anatomical_ids or age_onset_ids):
        return []
    
    data_model = repository.get_data_model()

    # Extract disease IDs from the data model
    disease_ids = set(disease['id'] for disease in data_model['diseases'])

    if phenotype_ids:
        initial_phenotype_id = phenotype_ids[0]
        phenotype_disease_ids = set(data_model['phenotype_to_diseases'].get(initial_phenotype_id, []))
        for phenotype_id in phenotype_ids[1:]:
            current_disease_ids = set(data_model['phenotype_to_diseases'].get(phenotype_id, []))
            phenotype_disease_ids.intersection_update(current_disease_ids)
        disease_ids.intersection_update(phenotype_disease_ids)

    if anatomical_ids:
        initial_anatomical_id = anatomical_ids[0]
        anatomical_disease_ids = set(data_model['anatomical_to_diseases'].get(initial_anatomical_id, []))
        for anatomical_id in anatomical_ids[1:]:
            current_disease_ids = set(data_model['anatomical_to_diseases'].get(anatomical_id, []))
            anatomical_disease_ids.intersection_update(current_disease_ids)
        disease_ids.intersection_update(anatomical_disease_ids)

    if age_onset_ids:
        initial_age_onset_id = age_onset_ids[0]
        age_onset_disease_ids = set(data_model['age_onset_to_diseases'].get(initial_age_onset_id, []))
        for age_onset_id in age_onset_ids[1:]:
            current_disease_ids = set(data_model['age_onset_to_diseases'].get(age_onset_id, []))
            age_onset_disease_ids.intersection_update(current_disease_ids)
        disease_ids.intersection_update(age_onset_disease_ids)

    diseases = [disease for disease in data_model['diseases'] if disease['id'] in disease_ids]

    for disease in diseases:
        if phenotype_ids:
            disease['phenotypes'] = [phenotype for phenotype in disease['phenotypes'] if phenotype['target'] not in phenotype_ids]
        if anatomical_ids:
            disease['anatomical_structures'] = [anatomical for anatomical in disease['anatomical_structures'] if anatomical['target'] not in anatomical_ids]
        if age_onset_ids:
            disease['age_onsets'] = [age_onset for age_onset in disease['age_onsets'] if age_onset['target'] not in age_onset_ids]

    return diseases

# load model files
def load_json_from_mongo(filename):
    with tempfile.NamedTemporaryFile() as temp_file:
        with repository.fs.get_last_version(filename) as file_data:
            temp_file.write(file_data.read())
            temp_file.flush()
            return joblib.load(temp_file.name)
        
def get_phenotypes():
    """
    Retrieve a list of unique phenotypes from the data model.
    Returns: a list of dictionaries representing unique phenotypes. Each dictionary contains:
          - The label of the phenotype.
          - The identifier of the phenotype, with the URL prefix removed.
    """

    phenotypes = []
    for disease in repository.get_data_model()['diseases']:
        for phenotype in disease.get('phenotypes', []):
            phenotypes.append({
                "label": phenotype.get('label', 'Unknown Phenotype'),
                "value": phenotype['target'].replace("http://purl.obolibrary.org/obo/", "")
            })
    
    # Remove duplicates
    unique_phenotypes = {v['value']: v for v in phenotypes}.values()
    return list(unique_phenotypes)

def get_anatomical_structures():
    """
    Retrieve a list of unique anatomical_structure from the data model.
    Returns: a list of dictionaries representing unique anatomical_structures. Each dictionary contains:
          - The label of the anatomical_structure.
          - The identifier of the anatomical_structure, with the URL prefix removed.
    """

    anatomical_structures = []
    for disease in repository.get_data_model()['diseases']:
        for anatomical_structure in disease.get('anatomical_structures', []):
            anatomical_structures.append({
                "label": anatomical_structure.get('label', 'Unknown anatomical structure'),
                "value": anatomical_structure['target'].replace("http://purl.obolibrary.org/obo/", "")
            })
    
    # Remove duplicates
    unique_anatomical_structures = {v['value']: v for v in anatomical_structures}.values()
    return list(unique_anatomical_structures)

def get_age_onsets():
    """
    Retrieve a list of unique age_onsets from the data model.
    Returns: a list of dictionaries representing unique age_onsets. Each dictionary contains:
          - The label of the age_onsets.
          - The identifier of the age_onsets, with the URL prefix removed.
    """
    age_onsets = []
    for disease in repository.get_data_model()['diseases']:
        for age_onset in disease.get('age_onsets', []):
            age_onsets.append({
                "label": age_onset.get('label', 'Unknown age onset'),
                "value": age_onset['target'].replace("http://purl.obolibrary.org/obo/", "")
            })

    # Remove duplicates
    unique_age_onsets = {v['value']: v for v in age_onsets}.values()
    return list(unique_age_onsets)

# get phenotype by id
def get_phenotype_by_id(full_id):
    return repository.get_phenotype_by_id(full_id)

# get anatomical by id
def get_anatomical_by_id(full_id):
    return repository.get_anatomical_by_id(full_id)
  

def update_data_model(full_disease_id, full_new_relationship_property, predicted_target):
    
    phenotype = get_phenotype_by_id(predicted_target) if constants.HP_STR in predicted_target else None
    anatomical_structure = get_anatomical_by_id(predicted_target) if constants.UBERON_STR in predicted_target else None

    data_model = repository.get_data_model()
    relationship_type = data_model["relationships_types"].get(full_new_relationship_property)

    # Actualizar el diccionario correspondiente
    if relationship_type == constants.HP_STR:
        phenotype_to_diseases = data_model["phenotype_to_diseases"].get(predicted_target, [])
        if full_disease_id not in phenotype_to_diseases:
            phenotype_to_diseases.append(full_disease_id)
        data_model["phenotype_to_diseases"][predicted_target] = phenotype_to_diseases
    elif relationship_type == constants.UBERON_STR:
        anatomical_to_diseases = data_model["anatomical_to_diseases"].get(predicted_target, [])
        if full_disease_id not in anatomical_to_diseases:
            anatomical_to_diseases.append(full_disease_id)
        data_model["anatomical_to_diseases"][predicted_target] = anatomical_to_diseases

    for disease in data_model["diseases"]:
        if disease["id"] == full_disease_id:
            if relationship_type == constants.HP_STR and phenotype:
                if "phenotypes" not in disease:
                    disease["phenotypes"] = []
                disease["phenotypes"].append(utils.create_relationship_entry(
                    "has_relationship", 
                    full_new_relationship_property, 
                    predicted_target, 
                    phenotype["name"], True))
                
            elif relationship_type == constants.UBERON_STR and anatomical_structure:
                 if "anatomical_structures" not in disease:
                     disease["anatomical_structures"] = []
                 disease["anatomical_structures"].append(utils.create_relationship_entry(
                    "has_relationship", 
                    full_new_relationship_property, 
                    predicted_target, 
                    anatomical_structure["name"], True))
            break

    disease_dict = {disease["id"]: disease for disease in data_model["diseases"]}
    repository.save_data_model(data_model)
    repository.save_disease_dict(disease_dict)

def get_phenotype_details_by_id_sparql(hp_id):

    sparql_query = constants.LABEL_QUERY.replace("HP_0000000", hp_id)
    #graph = repository.get_hpo_kg()
    #results = graph.query(sparql_query)
    results = []
    result_list = []
    for row in results:
        result_list.append({str(var): str(row[var]) for var in row.labels})
    return result_list