import utils
import models.random_forest as random_forest
import models.dbscan as dbscan
import models.hdbscan as hdbscan
import models.gradient_boost as gradient_boost
import constants
import services

import repository

def create_mondo_entry(id, name="Unknown", description="No description available", tracker_item=None):
    entry = {
        "id": id,
        "name": name,
        "description": description,
        "title": "Titulo de la enfermedad",
        "causes": ["Causa de la enfermedad #1", "Causa de la enfermedad #2", "Causa de la enfermedad #3"],
        "treatments": [],
        "anatomical_structures": [],
        "phenotypes": [],
        "exposures": [],
        "chemicals": [],
        "age_onsets": [],
        "children": [],
        "parent": None
    }
    if tracker_item:
        entry["tracker_item"] = tracker_item
    return entry

def create_entry(id, name="Unknown", description="No description available"):
    entry = {
        "id": id,
        "name": name,
        "description": description,
    }
    return entry

def build_is_a_hierarchy(mondo_data):
    '''
    Creates hierarchy of is_a relationships. Parent-Child
    epilepsy of type 1 is children of epilepsy. 
    '''
    is_a_hierarchy = {}
    for edge in mondo_data['graphs'][0]['edges']:
        if edge['pred'] == constants.IS_A_RELATIONSHIP:
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

def process_nodes(mondo_data, disease_dict, phenotype_dict, anatomical_dict, ro_dict, ecto_dict, maxo_dict, chebi_dict):

    # iterate nodes, get diseases (MONDO ID terms)
    for node in mondo_data['graphs'][0]['nodes']:

        node_id = node.get('id')

        # name and desc placeholders
        name = node.get('lbl', "Unknown Entity")
        description = "No description available"
        if 'meta' in node and 'definition' in node['meta']:
            description = node['meta']['definition'].get('val', description)

        # Excluir entidades obsoletas o de animales no humanos
        if "obsolete" in name.lower() or "non-human animal" in name.lower():
            continue

        # excluded entities, for example, top hierarchy nodes (MONDO:00000001 is disease, parent of them all)
        if node_id in constants.OMIT_ENTITIES:
            continue

        # phenotypes
        if "HP_" in node_id:
            phenotype_entry = create_entry(node_id, name, description)
            phenotype_dict[node_id] = phenotype_entry
            continue

        # anatomical_structures
        if "UBERON_" in node_id:
            anatomical_entry = create_entry(node_id, name, description)
            anatomical_dict[node_id] = anatomical_entry
            continue

        # Relations Ontology (RO)
        if "RO_" in node_id:
            ro_entry = create_entry(node_id, name, description)
            ro_dict[node_id] = ro_entry
            continue

        # ECTO Ontology
        if "ECTO_" in node_id:
            ecto_entry = create_entry(node_id, name, description)
            ecto_dict[node_id] = ecto_entry
            continue

        # MAXO Ontology
        if "MAXO_" in node_id:
            entry = create_entry(node_id, name, description)
            maxo_dict[node_id] = entry
            continue

        # CHEBI Ontology
        if "CHEBI_" in node_id:
            entry = create_entry(node_id, name, description)
            chebi_dict[node_id] = entry
            continue

        # excluded triples
        # TODO: use regex
        if not node_id or constants.MONDO_STR not in node_id:
            continue

        # tracker item is the pull request where the disease has been added
        tracker_item = None
        if 'meta' in node and 'basicPropertyValues' in node['meta']:
            for bpv in node['meta']['basicPropertyValues']:
                if bpv['pred'] == constants.TRACK_ITEM_REL_TYPE:
                    tracker_item = bpv['val']
                    break

        if node_id not in disease_dict:
            disease_entry = create_mondo_entry(node_id, name, description, tracker_item)
            disease_dict[node_id] = disease_entry
        else:
            disease_entry = disease_dict[node_id]
            disease_entry['name'] = name
            disease_entry['description'] = description
            if tracker_item:
                disease_entry['tracker_item'] = tracker_item

def process_edges(mondo_data, age_onset_hierarchy, disease_dict, data_model, ro_dict, ecto_dict, maxo_dict, chebi_dict):

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

        # TODO check this limitation
        if property_id in constants.SUB_OF_PROPERTIES or object_id in constants.OMIT_ENTITIES:
            continue

        # only process relationships whose subject entity contains "MONDO" in its ID 
        if subject_id and property_id and object_id and constants.MONDO_STR in subject_id:
            if subject_id in disease_dict:
                disease_entry = disease_dict[subject_id]

                # TODO add source of addition
                '''{
                    "sub" : "http://purl.obolibrary.org/obo/MONDO_1010420",
                    "pred" : "is_a",
                    "obj" : "http://purl.obolibrary.org/obo/MONDO_1010003",
                    "meta" : {
                        "basicPropertyValues" : [ {
                        "pred" : "http://www.geneontology.org/formats/oboInOwl#source",
                        "val" : "OMIA:000703"
                        }, {
                        "pred" : "http://www.geneontology.org/formats/oboInOwl#source",
                        "val" : "https://orcid.org/0000-0002-5002-8648"
                        } ]
                    }
                } '''


                # TODO gene relationship
                # Gene relationship
                #    Wiedemann-Steiner syndrome
                #    has material basis in germline mutation in
                #    KMT2A

                '''{
                    "sub" : "http://purl.obolibrary.org/obo/MONDO_0011518",
                    "pred" : "http://purl.obolibrary.org/obo/RO_0004003",
                    "obj" : "http://identifiers.org/hgnc/7132",
                    "meta" : {
                        "basicPropertyValues" : [ {
                        "pred" : "http://www.geneontology.org/formats/oboInOwl#source",
                        "val" : "MONDO:mim2gene_medgen"
                        } ]
                    }
                }'''


                relationship_type = "has_relationship"
                object_label = node_labels.get(object_id, 'Unknown')

                relationship_entry = utils.create_relationship_entry(relationship_type, property_id, object_id, object_label)

                # TODO axel include GO relationships, discover new features to expand the model

                # Medical Actions Ontology
                if constants.MAXO_STR in object_id:
                    if relationship_entry not in disease_entry["treatments"]:
                        disease_entry["treatments"].append(relationship_entry)
                        if object_id not in data_model["treatments"]:
                            data_model["treatments"][object_id] = []
                        data_model["treatments"][object_id].append(subject_id)
                    
                    new_rel = {"type": constants.MAXO_STR, "target": property_id, "label": ""}
                    if property_id not in relationships_types:
                        relationships_types[property_id] = []
                    if new_rel not in relationships_types[property_id]:
                        relationships_types[property_id].append(new_rel)

                # Anatomical Parts
                elif constants.UBERON_STR in object_id:
                    if relationship_entry not in disease_entry["anatomical_structures"]:
                        disease_entry["anatomical_structures"].append(relationship_entry)
                        if object_id not in data_model["anatomical_structures"]:
                            data_model["anatomical_structures"][object_id] = []
                        data_model["anatomical_structures"][object_id].append(subject_id)
                    
                    new_rel = {"type": constants.UBERON_STR, "target": property_id, "label": ""}
                    if property_id not in relationships_types:
                        relationships_types[property_id] = []
                    if new_rel not in relationships_types[property_id]:
                        relationships_types[property_id].append(new_rel)

                # Age Onset
                elif constants.HP_STR in object_id and object_id in age_onset_hierarchy:
                    if relationship_entry not in disease_entry["age_onsets"]:
                        disease_entry["age_onsets"].append(relationship_entry)
                        if object_id not in data_model["age_onsets"]:
                            data_model["age_onsets"][object_id] = []
                        data_model["age_onsets"][object_id].append(subject_id)
                    
                    new_rel = {"type": constants.HP_STR, "target": property_id, "label": ""}
                    if property_id not in relationships_types:
                        relationships_types[property_id] = []
                    if new_rel not in relationships_types[property_id]:
                        relationships_types[property_id].append(new_rel)


                # Penotypes
                elif constants.HP_STR in object_id:
                    if relationship_entry not in disease_entry["phenotypes"]:
                        disease_entry["phenotypes"].append(relationship_entry)
                        if object_id not in data_model["phenotypes"]:
                            data_model["phenotypes"][object_id] = []
                        data_model["phenotypes"][object_id].append(subject_id)

                    new_rel = {"type": constants.HP_STR, "target": property_id, "label": ""}
                    if property_id not in relationships_types:
                        relationships_types[property_id] = []
                    if new_rel not in relationships_types[property_id]:
                        relationships_types[property_id].append(new_rel)


                # Environmental Exposures, Conditions, Treatments 
                elif constants.ECTO_STR in object_id:
                    if relationship_entry not in disease_entry["exposures"]:
                        disease_entry["exposures"].append(relationship_entry)
                        if object_id not in data_model["exposures"]:
                            data_model["exposures"][object_id] = []
                        data_model["exposures"][object_id].append(subject_id)
                    
                    new_rel = {"type": constants.ECTO_STR, "target": property_id, "label": ""}
                    if property_id not in relationships_types:
                        relationships_types[property_id] = []
                    if new_rel not in relationships_types[property_id]:
                        relationships_types[property_id].append(new_rel)

                # Chemicals
                elif constants.CHEBI_STR in object_id:
                    if relationship_entry not in disease_entry["chemicals"]:
                        disease_entry["chemicals"].append(relationship_entry)
                        if object_id not in data_model["chemicals"]:
                            data_model["chemicals"][object_id] = []
                        data_model["chemicals"][object_id].append(subject_id)
                    
                    new_rel = {"type": constants.CHEBI_STR, "target": property_id, "label": ""}
                    if property_id not in relationships_types:
                        relationships_types[property_id] = []
                    if new_rel not in relationships_types[property_id]:
                        relationships_types[property_id].append(new_rel)

                # TODO rest of relationships, GO
                #else:
                    # Only add non-MAXO, non-UBERON, and non-HP relationships to the relationships field
                 #   if relationship_entry not in disease_entry['relationships']:
                  #      disease_entry['relationships'].append(relationship_entry)
    
    data_model["relationships_types"] = relationships_types


def data_augmentation(data_model, disease_dict, phenotypes_dict, anatomical_dict, ecto_dict, maxo_dict, chebi_dict, age_onset_hierarchy): 
    triples_to_add = [
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0000986", # pleurisy
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0002048", #lung
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0000986",  # pleurisy
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0001443", # chest
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0000986", # pleurisy
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0003621", #juvenile onset
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0000986", # pleurisy
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0003581", #adult onset
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0000986", # pleurisy
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0012531", # pain
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0000986", # pleurisy
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0002098", # Respiratory distress
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0000986", # pleurisy
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0012735", # Cough
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0000986", # pleurisy
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0001945", # Fever
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0000986", # pleurisy
            "property": "http://purl.obolibrary.org/obo/mondo#disease_responds_to", # has characteristic
            "target": "http://purl.obolibrary.org/obo/MAXO_0000221", #  # treatment: Treatment might include anti-inflammatories (NSAIDs), pain relievers and rest.
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0000986", # pleurisy
            "property": "http://purl.obolibrary.org/obo/mondo#disease_responds_to", # has characteristic
            "target": "http://purl.obolibrary.org/obo/MAXO_0000169", #  # treatment: generic anti inflamatory.
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0000986", # pleurisy
            "property": "http://purl.obolibrary.org/obo/mondo#predisposes_towards", # has characteristic
            "target": "http://purl.obolibrary.org/obo/MONDO_0005242", #  pus in pleural space (lungs)
        },

        ## PNEUMONIA
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005249", # pneumonia
            "property": "http://purl.obolibrary.org/obo/mondo#predisposes_towards", # has characteristic
            "target": "http://purl.obolibrary.org/obo/MONDO_0005242", #  pus in pleural space (lungs)
        },      
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005249", # pneumonia
            "property": "http://purl.obolibrary.org/obo/mondo#disease_responds_to", # has characteristic
            "target": "http://purl.obolibrary.org/obo/MAXO_0000061", #  # treatment: antibiotics to kill bacteria
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005249", # pneumonia
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0012531", # pain
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005249", # pneumonia
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0002098", # Respiratory distress
        },
                {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005249", # pneumonia
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0002048", #lung
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005249", # pneumonia
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0001443", # chest
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005249", # pneumonia
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0001945", # Fever
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005249", # pneumonia
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0001944", # Dehydratation
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005249", # pneumonia
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0030829", # Abnormal Breath-Sound
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005249", # pneumonia
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0030828", # Wheezing  A high-pitched whistling sound associated with labored breathi
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005249", # pneumonia
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0001649", # Tachycardia
        }, 
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005249", # pneumonia
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0002017", # Nausea and vomitting
        },    

        # PLEUROPNEUMONIA
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0001940", # pleuropneumonia
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0002102", # pleuritis
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0001940", # pleuropneumonia
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0012531", # pain
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0001940",  # pleuropneumonia
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0001443", # chest
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0001940", # pleuropneumonia
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0002048", #lung
        },




        ## Clostridium difficile colitis
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0000705", # Clostridium difficile colitis
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0012531", # pain
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0000705", # Clostridium difficile colitis
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0002027", # abdominal pain
        },
         {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0000705", # Clostridium difficile colitis
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0003549", # increases connective tissue
        },


        # eosinophilia-myalgia syndrome
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0004941", # eosinophilia-myalgia syndrome
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0012531", # pain
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0004941", # eosinophilia-myalgia syndrome
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0020064", # Abnormal eosinophil count
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0004941", # eosinophilia-myalgia syndrome
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0002048", #lung
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MMONDO_0004941", # eosinophilia-myalgia syndrome
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0001443", # chest
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0004941", # eosinophilia-myalgia syndrome
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0000948", #heart
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0004941", # eosinophilia-myalgia syndrome
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0001981", # blood vessels
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0004941", # eosinophilia-myalgia syndrome
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0001572", # hyoglossus muscle
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0004941", # eosinophilia-myalgia syndrome
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0000014", # skin
        },

        

        # stage I endometrioid carcinoma
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0004961", # stage I endometrioid carcinoma
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0012531", # pain
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0004961", # stage I endometrioid carcinoma
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0003444", # pelvis nerve
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0004961", # stage I endometrioid carcinoma
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0001255", # urine bladder
        },
        {
           "disease": "http://purl.obolibrary.org/obo/MONDO_0004961", # stage I endometrioid carcinoma
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0001295", # endometrium
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0004961", # stage I endometrioid carcinoma
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_6000315", # post menopausal onset
        },

        # stage II endometrioid carcinoma
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0004962", # stage II endometrioid carcinoma
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0012531", # pain
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0004962", # stage II endometrioid carcinoma
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0003444", # pelvis nerve
        },
        {
           "disease": "http://purl.obolibrary.org/obo/MONDO_0004962", # stage II endometrioid carcinoma
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0001255", # urine bladder
        },
        {
           "disease": "http://purl.obolibrary.org/obo/MONDO_0004962", # stage II endometrioid carcinoma
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0000996", # vagina
        },
        {
           "disease": "http://purl.obolibrary.org/obo/MONDO_0004962", # stage II endometrioid carcinoma
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0001295", # endometrium
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0004962", # stage II endometrioid carcinoma
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_6000315", # post menopausal onset
        },


         # adenoid cystic carcinoma
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0004971", #  adenoid cystic carcinoma
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0012531", # pain
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0004971", # adenoid cystic carcinoma
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0012532", # chronic pain
        },
        {
           "disease": "http://purl.obolibrary.org/obo/MONDO_0004971", # adenoid cystic carcinoma
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0003914", # ephitelial tube
        },


         # adrenal gland pheochromocytoma
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0004971", # adrenal gland pheochromocytoma
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0012531", # pain
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0004971", # adrenal gland pheochromocytoma
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0012532", # chronic pain
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0004971", # adrenal gland pheochromocytoma
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0002027", # abdominal pain
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0004971", # adrenal gland pheochromocytoma
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0002315", # headaches
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0004971", # adrenal gland pheochromocytoma
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0001962", # palpitations
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0004971",  # adrenal gland pheochromocytoma
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0001443", # chest
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0004971",  # adrenal gland pheochromocytoma
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0001945", # Fever
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0004971",  # adrenal gland pheochromocytoma
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0001337", # Tremor
        },

        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0004971",  # adrenal gland pheochromocytoma
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0000822", # Hypertension
        },


         # chronic pancreatitis
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005003", # chronic pancreatitis
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0012531", # pain
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005003", # chronic pancreatitis
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0012532", # chronic pain
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005003", # chronic pancreatitis
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0002027", # abdominal pain
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005003", # chronic pancreatitis
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0002024", # malabsorbtion
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005003", # chronic pancreatitis
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0000819", # diabetes mellitus
        },



         # irritable bowel syndrome
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005052", # irritable bowel syndrome
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0012531", # pain
        },

        # lung adenocarcinoma
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005061", # lung adenocarcinoma
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0012531", # pain
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005061", # lung adenocarcinoma
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0002048", #lung
        },


        # malignant pleural mesothelioma
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005112", # malignant pleural mesothelioma
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0012531", # pain
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005112", # malignant pleural mesothelioma
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0002048", #lung
        },


        # anthrax infection
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005119", # anthrax infection
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0012531", # pain
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005119", # anthrax infection
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0002048", #lung
        },
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005119", # anthrax infection
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0001945", # Fever
        },
                {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005119", # anthrax infection
            "property": "http://purl.obolibrary.org/obo/RO_0000053", # has characteristic
            "target": "http://purl.obolibrary.org/obo/HP_0002315", # headaches
        },
                {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005119", # anthrax infection
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0001443", # chest
        },

        # lung carcinoma
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005138", # lung carcinoma
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0002048", #lung
        },


        # pulmonary hypertension
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005149",
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0002048", #lung
        },


        # choriocarcinoma
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005207",
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0002048", #lung
        },


        # lung disorder
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005275",
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0002048", #lung
        },


        # pulmonary embolism
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005279",
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0002048", #lung
        },

         # lung neuroendocrine neoplasm
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005454",
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0002048", #lung
        },


         # chronic bronchitis
        {
            "disease": "http://purl.obolibrary.org/obo/MONDO_0005607",
            "property": "http://purl.obolibrary.org/obo/RO_0001025", # has location in
            "target": "http://purl.obolibrary.org/obo/UBERON_0002048", #lung
        },

        

        
    ]

    for triple in triples_to_add:
        # validate rel type before add
        rtype, lbl = services.get_details(triple["target"], disease_dict, phenotypes_dict, anatomical_dict, ecto_dict, maxo_dict, chebi_dict, age_onset_hierarchy)
        services.add_da_relationship(
            data_model,
            disease_dict,
            subject_id=triple["disease"],
            relationship_property=triple["property"],
            target_id=triple["target"],
            label=lbl,
            relationship_type=rtype
        )


    # default onsets
    default_age_onsets = [
        {
            "id": "http://purl.obolibrary.org/obo/HP_0003581",
            "label": "Adult Onset"
        },
         {
            "id": "http://purl.obolibrary.org/obo/HP_0011462",
            "label": "Neonatal Onset"
        },
         {
            "id": "http://purl.obolibrary.org/obo/HP_0011463",
            "label": "Congenital Onset"
        },
         {
            "id": "http://purl.obolibrary.org/obo/HP_0003593",
            "label": "Adolescent Onset"
        },
         {
            "id": "http://purl.obolibrary.org/obo/HP_0003584",
            "label": "Childhood Onset"
        },
        {
            "id": "http://purl.obolibrary.org/obo/HP_0003596",
            "label": "Middleage Onset"
        },
    ]

   
    # for disease_id, disease_entry in data_model.items():
    #     if not disease_entry["age_onsets"]:
    #         for onset in default_age_onsets:
    #             onset_id = onset["id"]
    #             relationship_entry = {
    #                 "type": "has_relationship",
    #                 "property": constants.HAS_CHARACTERISTIC_REL_TYPE,
    #                 "target": onset_id,
    #                 "label": onset["label"],
    #                 "predicted": False 
    #             }
    #             disease_entry["age_onsets"].append(relationship_entry)

    #             # Actualiza el data model
    #             if onset_id not in data_model["age_onsets"]:
    #                 data_model["age_onsets"][onset_id] = []
    #             if disease_id not in data_model["age_onsets"][onset_id]:
    #                 data_model["age_onsets"][onset_id].append(disease_id)

    #             print("added ageonset for " + disease_id)




def main():
    mondo_data = utils.load_json('datasets/mondo/mondo.json')

    age_onset_hierarchy = {
        constants.AGE_ONSET_PARENT_REL_TYPE: "Onset"
    }

    data_model = {
        "phenotypes": {},
        "age_onsets": {},
        "anatomical_structures": {},
        "treatments": {},
        "exposures": {},
        "chemicals": {},
        "relationships_types": {}
    }

    disease_dict = {}
    phenotypes_dict = {}
    anatomical_dict = {}
    ro_dict = {}
    ecto_dict = {}
    maxo_dict = {}
    chebi_dict = {}

    # TODO refactor hierarchy generated data
    # Build hierarchies
    is_a_hierarchy = build_is_a_hierarchy(mondo_data)
    onset_descendants = get_all_descendants(constants.AGE_ONSET_PARENT_REL_TYPE, is_a_hierarchy)
    for desc in onset_descendants:
        age_onset_hierarchy[desc] = "Onset"

    # Process data
    process_nodes(mondo_data, disease_dict, phenotypes_dict, anatomical_dict, ro_dict, ecto_dict, maxo_dict, chebi_dict) # TODO exclude obsolete terms from disease_dict
    process_edges(mondo_data, age_onset_hierarchy, disease_dict, data_model, ro_dict, ecto_dict, maxo_dict, chebi_dict)

    # data augmentation
    data_augmentation(data_model, disease_dict, phenotypes_dict, anatomical_dict, ecto_dict, maxo_dict, chebi_dict, age_onset_hierarchy)

    # Save to MongoDB
    repository.save(data_model, disease_dict, phenotypes_dict, anatomical_dict, ro_dict, ecto_dict, maxo_dict, chebi_dict)

    
    # train models
    # Random Forest alone
    random_forest.generate_model(None, False)
    # Random Forest specialized
    #random_forest_specialized.generate_models()
    # Random Forest + DBSCAN
    #random_forest.generate_model(dbscan.get_clustering_data_frame(), True)
    # Random Forest + HDBSCAN
    #random_forest.generate_model(hdbscan.get_clustering_data_frame(), True)
    

    # GradientBoost XGBoost alone
    #gradient_boost.generate_model(None, False)
    # GradientBoost + DBSCAN
    #gradient_boost.generate_model(dbscan.get_clustering_data_frame(), True)
    # Random GradientBoost + HDBSCAN
    ##gradient_boost.generate_model(hdbscan.get_clustering_data_frame(), True)

    # K-Means no porque no es aplicable a los datos, no son esfericos y hay ruido.

if __name__ == "__main__":
    main()
