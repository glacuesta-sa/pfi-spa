from db import data_model_collection

# Cargar el modelo de datos desde MongoDB
data_model = data_model_collection.find_one({}, {'_id': 0})
