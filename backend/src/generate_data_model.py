import utils
import models.random_forest as random_forest
import models.ontogpt as ontogpt
import constants
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS

import repository

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

def process_nodes(mondo_data, disease_dict):

    # iterate nodes, get diseases (MONDO ID terms)
    for node in mondo_data['graphs'][0]['nodes']:

        node_id = node.get('id')

        # name and desc placeholders
        name = node.get('lbl', "Unknown Disease")
        description = "No description available"
        if 'meta' in node and 'definition' in node['meta']:
            description = node['meta']['definition'].get('val', description)

        # excluded triples
        # TODO: use regex
        if not node_id or constants.MONDO_STR not in node_id:
            continue

        # excluded entities, for example, top hierarchy nodes (MONDO:00000001 is disease, parent of them all)
        if node_id in constants.OMIT_ENTITIES:
            continue

        # tracker item is the pull request where the disease has been added
        tracker_item = None
        if 'meta' in node and 'basicPropertyValues' in node['meta']:
            for bpv in node['meta']['basicPropertyValues']:
                if bpv['pred'] == constants.TRACK_ITEM_REL_TYPE:
                    tracker_item = bpv['val']
                    break

        if node_id not in disease_dict:
            disease_entry = create_entry(node_id, name, description, tracker_item)
            disease_dict[node_id] = disease_entry
        else:
            disease_entry = disease_dict[node_id]
            disease_entry['name'] = name
            disease_entry['description'] = description
            if tracker_item:
                disease_entry['tracker_item'] = tracker_item

def process_edges(mondo_data, age_onset_hierarchy, disease_dict, data_model):

    # TODO refactor node labels
    node_labels = {node['id']: node.get('lbl', 'Unknown') for node in mondo_data['graphs'][0]['nodes']}

    relationships_types = {}

    # iterate triples
    for triple in mondo_data['graphs'][0]['edges']:

        subject_id = triple.get('sub')
        property_id = triple.get('pred')
        object_id = triple.get('obj')

        # for children and parent fields, use is_a relationship
        if property_id == constants.IS_A_RELATIONSHIP and subject_id in disease_dict and object_id in disease_dict:
            disease_dict[subject_id]['parent'] = object_id
            if 'children' not in disease_dict[object_id]:
                disease_dict[object_id]['children'] = []
            disease_dict[object_id]['children'].append(subject_id)

        if property_id in constants.SUB_OF_PROPERTIES or object_id in constants.OMIT_ENTITIES:
            continue

        if subject_id and property_id and object_id and constants.MONDO_STR in subject_id:
            if subject_id in disease_dict:
                disease_entry = disease_dict[subject_id]
                relationship_type = "has_relationship"
                object_label = node_labels.get(object_id, 'Unknown')
                #relationship_entry = create_relationship_entry(relationship_type, property_id, object_id, object_label)

                # TODO axel ECTO relationships
                # TODO axel include ECTO, CHEBI, GO relationships, discover new features to expand the model
                # TODO axel, seggregate the collection in different documents. 
                # TODO axel, RO ontology? 
                '''or 'ECTO' in object_id'''
                if constants.MAXO_STR in object_id:
                    treatment_entry = {
                        "type": relationship_type,
                        "property": property_id,
                        "target": object_id,
                        "label": object_label
                    }
                    if treatment_entry not in disease_entry["treatments"]:
                        disease_entry["treatments"].append(treatment_entry)
                elif constants.UBERON_STR in object_id:
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

                    relationships_types[property_id] = constants.UBERON_STR

                elif constants.HP_STR in object_id and object_id in age_onset_hierarchy:
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
                    
                    relationships_types[property_id] = constants.HP_STR

                elif constants.HP_STR in object_id:
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
                    
                    relationships_types[property_id] = constants.HP_STR
                # TODO rest of relationships, CHEBI, GO
                #else:
                    # Only add non-MAXO, non-UBERON, and non-HP relationships to the relationships field
                 #   if relationship_entry not in disease_entry['relationships']:
                  #      disease_entry['relationships'].append(relationship_entry)
    
    data_model["relationships_types"] = relationships_types


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

def load_hp_ontology():

    # TODO: CI-CD generate .ttl 
    owl_file_path = "datasets/hpo/hp-base.owl"
    ttl_file_path = "datasets/hpo/hp-base.ttl"

    print('loading hpo ontology')

    # load owl, save ttl
    #g = Graph()
    #g.parse(owl_file_path, format='xml')
    
    # TODO en memoria por ahora
    repository.HPO_KG.serialize(destination=ttl_file_path, format='turtle')
 
    #with open(ttl_file_path, 'r') as file:
    #    ttl_data = file.read()

    #ttl_data_bytes = ttl_data.encode('utf-8')

    #repository.HPO_KG.parse(data=ttl_data_bytes, format='turtle')

    #repository.fs.put(ttl_data_bytes, filename="hpo.ttl")

def main():
    mondo_data = utils.load_json('datasets/mondo/mondo.json')

    age_onset_hierarchy = {
        constants.AGE_ONSET_PARENT_REL_TYPE: "Onset"
    }

    data_model = {
        "diseases": [],
        "phenotype_to_diseases": {},
        "age_onset_to_diseases": {},
        "anatomical_to_diseases": {},
        "relationships_types": {}
    }

    disease_dict = {}

    # TODO refactor hierarchy generated data
    # Build hierarchies
    is_a_hierarchy = build_is_a_hierarchy(mondo_data)
    onset_descendants = get_all_descendants(constants.AGE_ONSET_PARENT_REL_TYPE, is_a_hierarchy)
    for desc in onset_descendants:
        age_onset_hierarchy[desc] = "Onset"

    # Process data
    process_nodes(mondo_data, disease_dict) # TODO exclude obsolete terms from disease_dict
    process_edges(mondo_data, age_onset_hierarchy, disease_dict, data_model)
    finalize_data_model(disease_dict, data_model)

    # Save to MongoDB
    repository.save(data_model, disease_dict)

    # hpo ontology collection
    load_hp_ontology()

    # train models
    random_forest.generate_model()
    ontogpt.generate_model()


if __name__ == "__main__":
    main()
