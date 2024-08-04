import gridfs
from pymongo import MongoClient
import config

## MongoDB database conn
client = MongoClient(config.MONGO_URI)
db = client[config.MONDO_DB]
DISEASES_COLLECTION = db['diseases']
DATA_MODEL_COLLECTION = db['data_model']

# FileGrid conn
fs = gridfs.GridFS(db)

# TODO mongoDB adapter
# TODO DynamoDB adapter

# TODO move to repository, define interface
# diseases collection desde MongoDB
def get_diseases():
    diseases = DISEASES_COLLECTION.find({})
    return list(diseases)

# diseases collection desde MongoDB
def get_data_model():
    data_model = DATA_MODEL_COLLECTION.find_one({}, {'_id': 0})
    return data_model

# get disease by id
def get_disease_by_id(full_id):
    diseases = DISEASES_COLLECTION.find_one({"id": full_id}, {'_id': 0})
    return diseases

def save(data_model, disease_dict):
    """
    Save the data model and disease dictionary into MongoDB.

    This function clears existing data in the 'diseases' and 'data_model' collections and 
    inserts the new data.

    Parameters:
    data_model (dict): The data model to be saved.
    disease_dict (dict): A dictionary of disease entries to be saved.

    The function performs the following steps:
    1. Clears the existing documents
    2. Inserts the new disease data to collections.
    """
    # Clear existing collections
    DISEASES_COLLECTION.delete_many({})
    DATA_MODEL_COLLECTION.delete_many({})

    # Insert data
    DISEASES_COLLECTION.insert_many(disease_dict.values())
    DATA_MODEL_COLLECTION.insert_one(data_model)