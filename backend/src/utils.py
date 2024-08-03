import os
import tempfile
import time
from bson import ObjectId
import gridfs
import db
import openai
import joblib

from flask import json, jsonify, make_response

def convert_objectid_to_str(disease):
    if isinstance(disease, dict):
        for key, value in disease.items():
            if isinstance(value, ObjectId):
                disease[key] = str(value)
            elif isinstance(value, list):
                for item in value:
                    convert_objectid_to_str(item)
            elif isinstance(value, dict):
                convert_objectid_to_str(value)
    elif isinstance(disease, list):
        for item in disease:
            convert_objectid_to_str(item)
    return disease

def create_json_response(data, status_code=200):
    response = make_response(data, status_code)
    response.headers['Content-Type'] = 'application/json'
    return response

# Functions to build hierarchy from MongoDB data
def build_parent_child_hierarchy():
    diseases = list(db.diseases_collection.find({}, {'_id': 0}))
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

    for disease_id, disease in disease_dict.items():
        if disease['parent'] is None:
            add_to_hierarchy(disease_id, -1, disease['name'], 1, "#1d8bf8")
            for child_id in disease.get('children', []):
                process_hierarchy(child_id, id_map[disease_id])

    return hierarchy

def filter_hierarchy_by_mondo_id(mondo_id):
    diseases = list(db.diseases_collection.find({}, {'_id': 0}))
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

def get_diseases_by_phenotypes(phenotype_ids, data_model):
    """
    Retrieve all diseases associated with all of the given phenotypes, excluding the specified phenotypes from the phenotypes list.

    :param phenotype_ids: A list of phenotype IDs (HP IDs).
    :param data_model: The data model containing diseases and their relationships.
    :return: A list of diseases associated with all the given phenotypes.
    """
    if not phenotype_ids:
        return []

    print(f"Filtering diseases by phenotypes: {phenotype_ids}")

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

def get_diseases_by_age_onsets(age_onset_ids, data_model):
    """
    Retrieve all diseases associated with any of the given age onsets, excluding the specified age onsets from the age_onsets list.

    :param age_onset_ids: A list of age onset IDs (HP IDs).
    :param data_model: The data model containing diseases and their relationships.
    :return: A list of diseases associated with the given age onsets.
    """
    if not age_onset_ids:
        return []

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

def get_diseases_by_anatomical_structures(anatomical_ids, data_model):
    """
    Retrieve all diseases associated with any of the given anatomical structures, excluding the specified anatomical structures from the anatomical_structures list.

    :param anatomical_ids: A list of anatomical structure IDs (UBERON IDs).
    :param data_model: The data model containing diseases and their relationships.
    :return: A list of diseases associated with the given anatomical structures.
    """
    if not anatomical_ids:
        return []

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

def get_diseases_by_filters(phenotype_ids, anatomical_ids, age_onset_ids, data_model):
    if not (phenotype_ids or anatomical_ids or age_onset_ids):
        return []

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

def set_llm_fields(disease):

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


fs = gridfs.GridFS(db.db)

def load_json_from_mongo(filename):
    with fs.get_last_version(filename) as file_data:
        return json.loads(file_data.read().decode('utf-8'))

# Función para predecir relaciones
def predict_relationship(disease_id, relationship_type, relationship_property):

    # Función para esperar hasta que un archivo esté disponible en MongoDB
    def wait_for_file_in_mongo(filename, timeout=30):
        start_time = time.time()
        while not fs.exists({"filename": filename}):
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Timeout: {filename} no está disponible en MongoDB después de {timeout} segundos.")
            print(f"Esperando a que {filename} esté disponible en MongoDB...")
            time.sleep(5)
        print(f"{filename} está disponible en MongoDB.")

    # Archivos de modelo
    model_files = [
        'best_rf.pkl',
        'le_disease.pkl',
        'le_relationship_type.pkl',
        'le_relationship_property.pkl',
        'le_target_id.pkl',
        'le_disease_rel_prop.pkl'
    ]

    # Esperar a que todos los archivos de modelo estén disponibles en MongoDB
    for filename in model_files:
        wait_for_file_in_mongo(filename)

    # Cargar los archivos de modelo desde MongoDB
    def load_model_from_mongo(filename):
        with tempfile.NamedTemporaryFile() as temp_file:
            with fs.get_last_version(filename) as file_data:
                temp_file.write(file_data.read())
                temp_file.flush()
                return joblib.load(temp_file.name)

    best_rf = load_model_from_mongo('best_rf.pkl')
    le_disease = load_model_from_mongo('le_disease.pkl')
    le_relationship_type = load_model_from_mongo('le_relationship_type.pkl')
    le_relationship_property = load_model_from_mongo('le_relationship_property.pkl')
    le_target_id = load_model_from_mongo('le_target_id.pkl')
    le_disease_rel_prop = load_model_from_mongo('le_disease_rel_prop.pkl')


    # Codificar las entradas
    disease_id_encoded = le_disease.transform([disease_id])[0]
    relationship_type_encoded = le_relationship_type.transform([relationship_type])[0]
    relationship_property_encoded = le_relationship_property.transform([relationship_property])[0]

    # Crear la característica de interacción
    disease_rel_prop = f"{disease_id_encoded}_{relationship_property_encoded}"

    # Manejar etiquetas no vistas
    if disease_rel_prop not in le_disease_rel_prop.classes_:
        disease_rel_prop_encoded = -1
    else:
        disease_rel_prop_encoded = le_disease_rel_prop.transform([disease_rel_prop])[0]

    # Predecir el objetivo
    target_encoded = best_rf.predict([[disease_id_encoded, relationship_type_encoded, relationship_property_encoded, disease_rel_prop_encoded]])
    target = le_target_id.inverse_transform(target_encoded)

    return target[0]