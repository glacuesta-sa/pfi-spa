import json
import os
import tempfile

import config
import joblib
import repository
from pathlib import Path
import constants

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
    print(f"upload_to_datalake 1")
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
                print(f"upload_to_datalake FILE START")
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
    
     # Crea el directorio si no existe
    directory = os.path.dirname(local_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    try:
        if not os.path.exists(local_path):
            
            if not (config.AWS_ACCESS_KEY_ID and config.AWS_SECRET_ACCESS_KEY and config.S3_BUCKET_NAME):
                print("credenciales de aws invalidas. Falling back to MongoDB GridFS.")
                return load_json_from_gridfs(s3_key, local_path)
            
            config.s3_client.download_file(config.S3_BUCKET_NAME, s3_key, local_path)

        if not os.path.exists(local_path):
            if not (config.AWS_ACCESS_KEY_ID and config.AWS_SECRET_ACCESS_KEY and config.S3_BUCKET_NAME):
                print("credenciales de aws invalidas. Falling back to MongoDB GridFS.")
                return load_json_from_gridfs(s3_key, local_path)
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
        
def load_triples_from_json(file_path):
    with open(file_path, 'r') as f:
        triples = json.load(f)
    return triples

def data_augmentation(data_model, disease_dict, phenotypes_dict, anatomical_dict, ecto_dict, maxo_dict, chebi_dict, age_onset_hierarchy): 
    file_path = 'datasets/augmentation.json'
    triples_to_add = load_triples_from_json(file_path)

    for triple in triples_to_add:
        # validate rel type before add
        rtype, lbl = get_details(triple["target"], disease_dict, phenotypes_dict, anatomical_dict, ecto_dict, maxo_dict, chebi_dict, age_onset_hierarchy)
        add_da_relationship(
            data_model,
            disease_dict,
            subject_id=triple["disease"],
            relationship_property=triple["property"],
            target_id=triple["target"],
            label=lbl,
            relationship_type=rtype
        )

    # multimedia defaults
    #pleurisy
    add_multimedia_default(disease_dict, 
    "http://purl.obolibrary.org/obo/MONDO_0000986",
    "https://my.clevelandclinic.org/-/scassets/Images/org/health/articles/21172-pleuricy")
    
    #pleuropneumonia
    add_multimedia_default(disease_dict, 
    "http://purl.obolibrary.org/obo/MONDO_0001940",
    "https://www.researchgate.net/publication/336740103/figure/fig1/AS:817152022036481@1571835632789/Computed-tomography-picture-of-pleuropneumonia-in-Case-2.png")
    
    #eosinophilia-myalgia syndrome
    add_multimedia_default(disease_dict, 
    "http://purl.obolibrary.org/obo/MONDO_0004941",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTsYuEBpFkzqKfPBt7kfsV1jRCyWmFd-6xMqw&s")
    
    #lung adenocarcinoma
    add_multimedia_default(disease_dict, 
    "http://purl.obolibrary.org/obo/MONDO_0005061",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRpTPKiod6umFLYw1hat00kt1KovI7Oy0AHmQ&s")
    
    #malignant pleural mesothelioma
    add_multimedia_default(disease_dict, 
    "http://purl.obolibrary.org/obo/MONDO_0005112",
    "https://www.mesothelioma.com/wp-content/uploads/MESO_pleural_featured-68.svg")
    
    #anthrax infection
    add_multimedia_default(disease_dict, 
    "http://purl.obolibrary.org/obo/MONDO_0005119",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSccd6UMSitBM59MbVAs-S6woYf5-7YigFB2Q&s")

    #pneumonia
    add_multimedia_default(disease_dict, 
    "http://purl.obolibrary.org/obo/MONDO_0005249",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS54m28GvQ0HgZtTIzpSRMvHmssrk85Kcmr4A&s")

    #Clostridium difficile colitis
    add_multimedia_default(disease_dict, 
    "http://purl.obolibrary.org/obo/MONDO_0000705",
    "https://upload.wikimedia.org/wikipedia/commons/a/a1/Pseudomembranous_colitis.JPG")

    #stage I endometrioid carcinoma
    add_multimedia_default(disease_dict, 
    "http://purl.obolibrary.org/obo/MONDO_0004961",
    "https://www.researchgate.net/publication/258429939/figure/fig2/AS:297659274416129@1447978909584/Endometrioid-adenocarcinoma-grade-1-The-glandular-component-is-a-caricature-of.png")

    #stage II endometrioid carcinoma
    add_multimedia_default(disease_dict, 
    "http://purl.obolibrary.org/obo/MONDO_0004962",
    "https://www.researchgate.net/publication/258429939/figure/fig2/AS:297659274416129@1447978909584/Endometrioid-adenocarcinoma-grade-1-The-glandular-component-is-a-caricature-of.png")


    #adenoid cystic carcinoma
    add_multimedia_default(disease_dict, 
    "http://purl.obolibrary.org/obo/MONDO_0004971",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ6bdRXdjM5dUH0cODTLO0D6XU01_AOrVlhdA&s")

    #"chronic pancreatitis"
    add_multimedia_default(disease_dict, 
    "http://purl.obolibrary.org/obo/MONDO_0005003",
    "https://my.clevelandclinic.org/-/scassets/Images/org/health/articles/8103-pancreatitis-illustration")

    #"irritable bowel syndrome"
    add_multimedia_default(disease_dict, 
    "http://purl.obolibrary.org/obo/MONDO_0005052",
    "https://alpinesurgical.sg/wp-content/uploads/2023/10/ibs2-1.webp")

    # "neurological pain disorder"
    add_multimedia_default(disease_dict, 
    "http://purl.obolibrary.org/obo/MONDO_0700057",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6qG-aPhxJLuqjDU_20tEim0tkZWg6VXaPrw&s")
    
def add_multimedia_default(disease_dict, subject_id, link):
    """
    Add default multimedia
    """    
    # diseases collection
    disease_entry = disease_dict.get(subject_id)
    if not disease_entry:
        print(f"{subject_id} not found in the disease dictionary.")
        return

    disease_entry["multimedia"] = [link]

    print(f"added multimedia for disease {subject_id}: image link {link}.")

def get_details(target_id, diseases_dict, phenotypes_dict, anatomical_dict, ecto_dict, maxo_dict, chebi_dict, age_onset_hierarchy):
    """
    returns relationship type and label from dict
    """
    rtype = "invalid"

    if constants.UBERON_STR in target_id:
        rtype = "anatomical_structures"
    elif constants.HP_STR in target_id:
        rtype =  "phenotypes"
        if target_id in age_onset_hierarchy:
            rtype= "age_onsets"
    elif constants.ECTO_STR in target_id:
        rtype =  "exposures"
    elif constants.MAXO_STR in target_id:
        rtype =  "treatments"
    elif constants.CHEBI_STR in target_id:
        rtype = "chemicals"
    elif constants.MONDO_STR in target_id:
        rtype = "diseases"

    label = "dummy"
    if "anatomical" in rtype:
        dict = anatomical_dict
    elif "phenotype"  in rtype or "age_onset" in rtype:
        dict = phenotypes_dict
    elif "treatment"  in rtype:
        dict = maxo_dict
    elif "chemical"  in rtype:
        dict = chebi_dict
    elif "exposure" in rtype:
        dict = ecto_dict
    elif "diseases" in rtype:
        dict = diseases_dict

    entity = get_entity_by_dict_and_id(dict, target_id)
    if entity != None: 
        label = entity["name"]
    return rtype, label

# get generic entity by its dict and its id
def get_entity_by_dict_and_id(dict, full_id):

    entry = dict.get(full_id)
    if not entry:
        print(f"{full_id} not found in the dictionary.")
        return None
    return entry

def add_da_relationship(data_model, disease_dict, subject_id, relationship_property, target_id, label, relationship_type):
    """
    Add a data augmentation relationship to the specified disease in both the data model and diseases collection.

    
    """
    # data model    
    data_key = f"{relationship_type}"
    relationships = data_model.get(data_key, {})
    
    if target_id not in relationships:
        relationships[target_id] = []
    
    if subject_id not in relationships[target_id]:
        relationships[target_id].append(subject_id)
    
    data_model[data_key] = relationships
    
    # diseases collection
    disease_entry = disease_dict.get(subject_id)
    if not disease_entry:
        print(f"{subject_id} not found in the disease dictionary.")
        return
    
    relationship_entry = {
        "type": "has_relationship",
        "property": relationship_property,
        "target": target_id,
        "label": label,
        "predicted": False
    }
    
    if relationship_type not in disease_entry:
        disease_entry[relationship_type] = []
    
    if relationship_entry not in disease_entry[relationship_type]:
        disease_entry[relationship_type].append(relationship_entry)

    print(f"relationship added between {subject_id} and {target_id} under {relationship_type}.")