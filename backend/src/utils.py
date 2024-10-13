import json
import os
import tempfile

import config
import joblib
import repository
from pathlib import Path

from botocore.exceptions import ClientError

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

def upload_to_datalake(filename, model):
    
    if not (config.AWS_ACCESS_KEY_ID and config.AWS_SECRET_ACCESS_KEY and config.S3_BUCKET_NAME):
        print("error con credenciales de s3, forbidden. fallback a mongo grid fs.")
        return upload_to_gridfs(filename, model)

    try:

        # chequear si ya existe en el bucket
        config.s3_client.head_object(Bucket=config.S3_BUCKET_NAME, Key=filename)
        print(f"modelo {filename} ya existe en el bucket {config.S3_BUCKET_NAME}. Skip.")

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '403':
            print("error con credenciales de s3, forbidden. fallback a mongo grid fs.")
            return upload_to_gridfs(filename, model)
        if error_code == '404':
            with tempfile.NamedTemporaryFile() as temp_file:
                joblib.dump(model, temp_file.name)
                
                # subir a s3 si no existe ya
                config.s3_client.upload_file(
                    Filename=temp_file.name,
                    Bucket=config.S3_BUCKET_NAME,
                    Key=filename
                )
            print(f"subir archivo {filename} a bucket {config.S3_BUCKET_NAME}.")
        else:
            print("error inesperado. fallback a mongo grid fs.")
            return upload_to_gridfs(filename, model)

def upload_to_gridfs(filename, model):
    with tempfile.NamedTemporaryFile() as temp_file:
        joblib.dump(model, temp_file.name)
        with open(temp_file.name, 'rb') as file_data:
            repository.fs.put(file_data, filename=filename)
    print(f"modelo {filename} subido a mongo gridfs")

def load_json_from_datalake(s3_key, local_path):

    if not (config.AWS_ACCESS_KEY_ID and config.AWS_SECRET_ACCESS_KEY and config.S3_BUCKET_NAME):
        print("credenciales de aws invalidas. Falling back to MongoDB GridFS.")
        return load_json_from_gridfs(s3_key, local_path)

    # Crea el directorio si no existe
    directory = os.path.dirname(local_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    try:
        if not os.path.exists(local_path):
            config.s3_client.download_file(config.S3_BUCKET_NAME, s3_key, local_path)

        if not os.path.exists(local_path):
            raise FileNotFoundError(f"Downloaded file {local_path} not found.")
        
        model = joblib.load(local_path)
        return model
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '403':
            print("credenciales invalidas. Falling back to MongoDB GridFS.")
            return load_json_from_gridfs(s3_key, local_path)
        else:
            print("Error inesperado. Falling back to MongoDB GridFS.")
            return load_json_from_gridfs(s3_key, local_path)


def load_json_from_gridfs(filename, local_path):
    with tempfile.NamedTemporaryFile() as temp_file:
        with repository.fs.get_last_version(filename) as file_data:
            temp_file.write(file_data.read())
            temp_file.flush()
            return joblib.load(temp_file.name)
        