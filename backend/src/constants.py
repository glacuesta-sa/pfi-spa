# constants.py

# ENTITIES CONSTANTS
MONDO_STR = 'MONDO'
MAXO_STR = 'MAXO'
HP_STR = 'HP'
UBERON_STR = 'UBERON'
HP_NAME = 'The Human Phenotype Ontology'
UBERON_NAME = 'The Uber-anatomy ontology'

# RELATIONSHIP CONSTANTS
IS_A_RELATIONSHIP = 'is_a'
TRACK_ITEM_REL_TYPE = 'http://purl.obolibrary.org/obo/IAO_0000233'
AGE_ONSET_PARENT_REL_TYPE = 'http://purl.obolibrary.org/obo/HP_0003674'

# SPECIFIC PROPERTIES
SUB_OF_PROPERTIES = ['http://www.w3.org/2000/01/rdf-schema#subClassOf', 'subPropertyOf']

# OMITTED ENTITIES, i.e., ARE TOP HIERARCHY PARENT OR NON-HUMAN ANIMAL DISEASES 
OMIT_ENTITIES = {
    "http://purl.obolibrary.org/obo/MONDO_0000001",
    "http://purl.obolibrary.org/obo/HP_0000001",
    "http://purl.obolibrary.org/obo/MAXO_0000001",
    "http://purl.obolibrary.org/obo/UBERON_0000001"
}

# random forest files stored in fileGrid
RANDOM_FOREST_MODEL_FILES = [
    'best_rf.pkl',
    'le_disease.pkl',
    'le_relationship_type.pkl',
    'le_relationship_property.pkl',
    'le_target_id.pkl',
    'le_disease_rel_prop.pkl'
]
