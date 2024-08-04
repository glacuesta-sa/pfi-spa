from pymongo import MongoClient
from config import MONGO_URI, DATABASE_NAME

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
diseases_collection = db['diseases']
data_model_collection = db['data_model']

# diseases collection desde MongoDB
def get_diseases_collection():
    diseases = diseases_collection.find({})
    return diseases

# diseases collection desde MongoDB
def get_data_model():
    data_model = data_model_collection.find_one({}, {'_id': 0})
    return data_model

# get disease by id
def get_disease_by_id(full_id):
    diseases = diseases_collection.find_one({"id": full_id}, {'_id': 0})
    return diseases
