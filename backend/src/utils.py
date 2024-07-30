from bson import ObjectId
from db import diseases_collection
from models import data_model

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

# Functions to build hierarchy from MongoDB data
def build_parent_child_hierarchy():
    diseases = list(diseases_collection.find({}, {'_id': 0}))
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
    diseases = list(diseases_collection.find({}, {'_id': 0}))
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