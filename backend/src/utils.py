import json
import os
import services
from pathlib import Path
from bson import ObjectId

# load file
def load_json(file_path):
    file = None
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print("Current Working Directory:", os.getcwd())
        file_path = Path('/home/glacuesta/develop/repos/personal/pfi-spa/backend/datasets/mondo/mondo.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

# load sparql query from file
def load_sparql_query(file_path):
    with open(file_path, 'r') as file:
        return file.read()
    
def create_relationship_entry(rel_type, property_id, target_id, target_label, predicted=False):
    return {
        "type": rel_type,
        "property": property_id,
        "target": target_id,
        "label": target_label,
        "predicted": predicted
    }