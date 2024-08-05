import json
from bson import ObjectId

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

# load file
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# load sparql query from file
def load_sparql_query(file_path):
    with open(file_path, 'r') as file:
        return file.read()