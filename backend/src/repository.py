import time
import gridfs
from pymongo import MongoClient
import config

## TODO __init__ method

## MongoDB database conn
client = MongoClient(config.MONGO_URI)
db = client[config.MONDO_DB]
DISEASES_COLLECTION = db['diseases']
DATA_MODEL_COLLECTION = db['data_model']
PHENOTYPES_COLLECTION = db['phenotypes']
ANATOMICAL_COLLECTION = db['anatomical_structures']
RO_COLLECTION = db['relationships']
ECTO_COLLECTION = db['exposures']
MAXO_COLLECTION = db['treatments']
CHEBI_COLLECTION = db['chemicals']

# FileGrid conn
fs = gridfs.GridFS(db)

# TODO mongoDB adapter
# TODO DynamoDB adapter

# TODO move to repository, define interface
# diseases collection desde MongoDB
def get_diseases():
    print(f"get diseases")
    diseases = DISEASES_COLLECTION.find({})
    return list(diseases)

def get_diseases_ids():
    """
    Fetch all disease IDs from the DISEASES collection.
    
    Returns:
    list: A list of all disease IDs.
    """
    return DISEASES_COLLECTION.distinct("id")

def get_diseases_by_ids(filtered_disease_ids):
    """
    Fetch all disease from the DISEASES collection for the given list of ids
    
    Returns:
    list: A list of all disease IDs.
    """
    return list(DISEASES_COLLECTION.find({"id": {"$in": list(filtered_disease_ids)}}, {'_id': 0}))


# diseases collection desde MongoDB
def get_data_model():
    data_model = DATA_MODEL_COLLECTION.find_one({}, {'_id': 0})
    return data_model

# get disease by id
def get_disease_by_id(full_id):
    diseases = DISEASES_COLLECTION.find_one({"id": full_id}, {'_id': 0})
    return diseases

# get phenotype by id
def get_phenotype_by_id(full_id):
    phenotype = PHENOTYPES_COLLECTION.find_one({"id": full_id}, {'_id': 0})
    return phenotype

# get anatomical_structures by id
def get_anatomical_by_id(full_id):
    anatomical = ANATOMICAL_COLLECTION.find_one({"id": full_id}, {'_id': 0})
    return anatomical

# get relationship by id
def get_relationship_by_id(full_id):
    relationship = RO_COLLECTION.find_one({"id": full_id}, {'_id': 0})
    return relationship

# get exposure by id
def get_exposure_by_id(full_id):
    exppsure = ECTO_COLLECTION.find_one({"id": full_id}, {'_id': 0})
    return exppsure

# get treatment by id
def get_treatment_by_id(full_id):
    treat = MAXO_COLLECTION.find_one({"id": full_id}, {'_id': 0})
    return treat

# get chemical by id
def get_chemical_by_id(full_id):
    chemical = CHEBI_COLLECTION.find_one({"id": full_id}, {'_id': 0})
    return chemical

def save_data_model(data_model):
    DATA_MODEL_COLLECTION.delete_many({})
    DATA_MODEL_COLLECTION.insert_one(data_model)
    
def save_disease_dict(disease_dict):
    DISEASES_COLLECTION.delete_many({})
    DISEASES_COLLECTION.insert_many(disease_dict.values())
    
def save_phenotypes(phenotype_dict):
    PHENOTYPES_COLLECTION.delete_many({})
    PHENOTYPES_COLLECTION.insert_many(phenotype_dict.values())

def save_anatomical(anatomical_dict):
    ANATOMICAL_COLLECTION.delete_many({})
    ANATOMICAL_COLLECTION.insert_many(anatomical_dict.values())

def save_ro_dict(ro_dict):
    RO_COLLECTION.delete_many({})
    RO_COLLECTION.insert_many(ro_dict.values())

def save_ecto_dict(ecto_dict):
    ECTO_COLLECTION.delete_many({})
    ECTO_COLLECTION.insert_many(ecto_dict.values())

def save_maxo_dict(maxo_dict):
    MAXO_COLLECTION.delete_many({})
    MAXO_COLLECTION.insert_many(maxo_dict.values())

def save_chebi_dict(chebi_dict):
    CHEBI_COLLECTION.delete_many({})
    CHEBI_COLLECTION.insert_many(chebi_dict.values())

def save(data_model, disease_dict, phenotype_dict, anatomical_dict, ro_dict, ecto_dict, maxo_dict, chebi_dict):
    """
    Save the data model and associated relationships collections into MongoDB.
    """
    save_data_model(data_model)
    save_disease_dict(disease_dict)
    save_phenotypes(phenotype_dict)
    save_anatomical(anatomical_dict)
    save_ro_dict(ro_dict)
    save_ecto_dict(ecto_dict)
    save_maxo_dict(maxo_dict)
    save_chebi_dict(chebi_dict)

def wait_for_file_in_mongo(filename, timeout=300):
    """
    Wait until a specified file is available in MongoDB's GridFS.
    Is useful to avoid race condition with mongoDB

    Parameters:
    filename (str): The name of the file to wait for.
    timeout (int): The maximum time to wait for the file, in seconds.

    Raises:
    TimeoutError: If the file is not available within the timeout period.
    """
    start_time = time.time()
    while not fs.exists({"filename": filename}):
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Timeout: {filename} not available in mongoDB after {timeout} seconds.")
        print(f"Waiting for {filename} to be available in MongoDB...")
        time.sleep(5)
    print(f"{filename} is available MongoDB.")