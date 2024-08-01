from db import data_model_collection

# modelo de datos desde MongoDB
def get_data_model():
    data_model = data_model_collection.find_one({}, {'_id': 0})
    return data_model