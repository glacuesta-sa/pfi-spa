import json
from pymongo import MongoClient
import config

def load_mondo_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def create_entry(id, name="Unknown", description="No description available", tracker_item=None):
    entry = {
        "id": id,
        "name": name,
        "description": description,
        "title": "Titulo de la enfermedad",
        "causes": ["Causa de la enfermedad #1", "Causa de la enfermedad #2", "Causa de la enfermedad #3"],
        "treatments": [],
        "anatomical_structures": [],
        "phenotypes": [],
        "age_onsets": [],
        "children": [],
        "parent": None
    }
    if tracker_item:
        entry["tracker_item"] = tracker_item
    return entry

def create_relationship_entry(rel_type, property_id, target_id, target_label):
    return {
        "type": rel_type,
        "property": property_id,
        "target": target_id,
        "label": target_label
    }

def build_is_a_hierarchy(mondo_data):
    is_a_hierarchy = {}
    for edge in mondo_data['graphs'][0]['edges']:
        if edge['pred'] == 'is_a':
            if edge['obj'] not in is_a_hierarchy:
                is_a_hierarchy[edge['obj']] = []
            is_a_hierarchy[edge['obj']].append(edge['sub'])
    return is_a_hierarchy

def get_all_descendants(node, hierarchy):
    descendants = set()
    nodes_to_visit = [node]
    while nodes_to_visit:
        current_node = nodes_to_visit.pop()
        if current_node in hierarchy:
            children = hierarchy[current_node]
            descendants.update(children)
            nodes_to_visit.extend(children)
    return descendants

def process_nodes(mondo_data, omit_entities, disease_dict):
    for record in mondo_data['graphs'][0]['nodes']:
        defined_class_id = record.get('id')
        name = record.get('lbl', "Unknown Disease")
        description = "No description available"

        if 'meta' in record and 'definition' in record['meta']:
            description = record['meta']['definition'].get('val', description)

        if not defined_class_id or 'MONDO' not in defined_class_id:
            continue

        if defined_class_id in omit_entities:
            continue

        tracker_item = None
        if 'meta' in record and 'basicPropertyValues' in record['meta']:
            for bpv in record['meta']['basicPropertyValues']:
                if bpv['pred'] == 'http://purl.obolibrary.org/obo/IAO_0000233':
                    tracker_item = bpv['val']
                    break

        if defined_class_id not in disease_dict:
            disease_entry = create_entry(defined_class_id, name, description, tracker_item)
            disease_dict[defined_class_id] = disease_entry
        else:
            disease_entry = disease_dict[defined_class_id]
            disease_entry['name'] = name
            disease_entry['description'] = description
            if tracker_item:
                disease_entry['tracker_item'] = tracker_item

def process_edges(mondo_data, omit_entities, age_onset_hierarchy, disease_dict, data_model):
    node_labels = {node['id']: node.get('lbl', 'Unknown') for node in mondo_data['graphs'][0]['nodes']}
    
    for record in mondo_data['graphs'][0]['edges']:
        subject_id = record.get('sub')
        property_id = record.get('pred')
        object_id = record.get('obj')

        if property_id == 'is_a' and subject_id in disease_dict and object_id in disease_dict:
            disease_dict[subject_id]['parent'] = object_id
            if 'children' not in disease_dict[object_id]:
                disease_dict[object_id]['children'] = []
            disease_dict[object_id]['children'].append(subject_id)

        if property_id in ['http://www.w3.org/2000/01/rdf-schema#subClassOf', 'subPropertyOf'] or object_id in omit_entities:
            continue

        if subject_id and property_id and object_id and 'MONDO' in subject_id:
            if subject_id in disease_dict:
                disease_entry = disease_dict[subject_id]
                relationship_type = "has_relationship"
                object_label = node_labels.get(object_id, 'Unknown')
                relationship_entry = create_relationship_entry(relationship_type, property_id, object_id, object_label)

                if 'MAXO' in object_id:
                    treatment_entry = {
                        "type": relationship_type,
                        "property": property_id,
                        "target": object_id,
                        "label": object_label
                    }
                    if treatment_entry not in disease_entry["treatments"]:
                        disease_entry["treatments"].append(treatment_entry)
                elif 'UBERON' in object_id:
                    anatomical_entry = {
                        "type": relationship_type,
                        "property": property_id,
                        "target": object_id,
                        "label": object_label
                    }
                    if anatomical_entry not in disease_entry["anatomical_structures"]:
                        disease_entry["anatomical_structures"].append(anatomical_entry)

                        if object_id not in data_model["anatomical_to_diseases"]:
                            data_model["anatomical_to_diseases"][object_id] = []
                        data_model["anatomical_to_diseases"][object_id].append(subject_id)
                elif 'HP' in object_id and object_id in age_onset_hierarchy:
                    age_onset_entry = {
                        "type": relationship_type,
                        "property": property_id,
                        "target": object_id,
                        "label": object_label
                    }
                    if age_onset_entry not in disease_entry["age_onsets"]:
                        disease_entry["age_onsets"].append(age_onset_entry)

                        if object_id not in data_model["age_onset_to_diseases"]:
                            data_model["age_onset_to_diseases"][object_id] = []
                        data_model["age_onset_to_diseases"][object_id].append(subject_id)
                elif 'HP' in object_id:
                    phenotype_entry = {
                        "type": relationship_type,
                        "property": property_id,
                        "target": object_id,
                        "label": object_label
                    }
                    if phenotype_entry not in disease_entry["phenotypes"]:
                        disease_entry["phenotypes"].append(phenotype_entry)

                        if object_id not in data_model["phenotype_to_diseases"]:
                            data_model["phenotype_to_diseases"][object_id] = []
                        data_model["phenotype_to_diseases"][object_id].append(subject_id)


def finalize_data_model(disease_dict, data_model):
    for disease in disease_dict.values():
        if disease['treatments'] or disease['anatomical_structures'] or disease['phenotypes'] or disease['age_onsets']:
            if not disease['treatments']:
                del disease['treatments']
            if not disease['anatomical_structures']:
                del disease['anatomical_structures']
            if not disease['phenotypes']:
                del disease['phenotypes']
            if not disease['age_onsets']:
                del disease['age_onsets']
            data_model['diseases'].append(disease)

def save_to_mongodb(data_model, disease_dict, mongo_uri=config.MONGO_URI, db_name='mondo_db'):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    diseases_collection = db['diseases']
    data_model_collection = db['data_model']

    # Clear existing collections
    diseases_collection.delete_many({})
    data_model_collection.delete_many({})

    # Insert data
    diseases_collection.insert_many(disease_dict.values())
    data_model_collection.insert_one(data_model)

def main():
    mondo_data = load_mondo_data('datasets/mondo/mondo.json')

    omit_entities = {
        "http://purl.obolibrary.org/obo/MONDO_0000001",
        "http://purl.obolibrary.org/obo/HP_0000001",
        "http://purl.obolibrary.org/obo/MAXO_0000001",
        "http://purl.obolibrary.org/obo/UBERON_0000001"
    }

    age_onset_hierarchy = {
        "http://purl.obolibrary.org/obo/HP_0003674": "Onset"
    }

    data_model = {
        "diseases": [],
        "phenotype_to_diseases": {},
        "age_onset_to_diseases": {},
        "anatomical_to_diseases": {}
    }

    disease_dict = {}

    # Build hierarchies
    is_a_hierarchy = build_is_a_hierarchy(mondo_data)
    onset_descendants = get_all_descendants("http://purl.obolibrary.org/obo/HP_0003674", is_a_hierarchy)
    for desc in onset_descendants:
        age_onset_hierarchy[desc] = "Onset"

    # Process data
    process_nodes(mondo_data, omit_entities, disease_dict)
    process_edges(mondo_data, omit_entities, age_onset_hierarchy, disease_dict, data_model)
    finalize_data_model(disease_dict, data_model)

    # Save to MongoDB
    save_to_mongodb(data_model, disease_dict)

if __name__ == "__main__":
    main()
