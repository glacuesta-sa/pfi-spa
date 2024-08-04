import json
import tempfile
import gridfs
from pymongo import MongoClient
import config

import db
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from imblearn.over_sampling import RandomOverSampler
from scipy.stats import randint
import joblib

def load_mondo_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def create_entry(id, name="Unknown", description="No description available", tracker_item=None):
    entry = {
        "id": id,
        "name": name,
        "description": description,
        "title": "Titulo de la enfermedad",
        "causes": ["Causa de la enfermedad #1", "Causa de la enfermedad #2", "Causa de la enfermedad #3"],
        "treatments": [],
        "anatomical_structures": [],
        "phenotypes": [],
        "age_onsets": [],
        "children": [],
        "parent": None
    }
    if tracker_item:
        entry["tracker_item"] = tracker_item
    return entry

def create_relationship_entry(rel_type, property_id, target_id, target_label):
    return {
        "type": rel_type,
        "property": property_id,
        "target": target_id,
        "label": target_label
    }

def build_is_a_hierarchy(mondo_data):
    is_a_hierarchy = {}
    for edge in mondo_data['graphs'][0]['edges']:
        if edge['pred'] == 'is_a':
            if edge['obj'] not in is_a_hierarchy:
                is_a_hierarchy[edge['obj']] = []
            is_a_hierarchy[edge['obj']].append(edge['sub'])
    return is_a_hierarchy

def get_all_descendants(node, hierarchy):
    descendants = set()
    nodes_to_visit = [node]
    while nodes_to_visit:
        current_node = nodes_to_visit.pop()
        if current_node in hierarchy:
            children = hierarchy[current_node]
            descendants.update(children)
            nodes_to_visit.extend(children)
    return descendants

def process_nodes(mondo_data, omit_entities, disease_dict):
    for record in mondo_data['graphs'][0]['nodes']:
        defined_class_id = record.get('id')
        name = record.get('lbl', "Unknown Disease")
        description = "No description available"

        if 'meta' in record and 'definition' in record['meta']:
            description = record['meta']['definition'].get('val', description)

        if not defined_class_id or 'MONDO' not in defined_class_id:
            continue

        if defined_class_id in omit_entities:
            continue

        tracker_item = None
        if 'meta' in record and 'basicPropertyValues' in record['meta']:
            for bpv in record['meta']['basicPropertyValues']:
                if bpv['pred'] == 'http://purl.obolibrary.org/obo/IAO_0000233':
                    tracker_item = bpv['val']
                    break

        if defined_class_id not in disease_dict:
            disease_entry = create_entry(defined_class_id, name, description, tracker_item)
            disease_dict[defined_class_id] = disease_entry
        else:
            disease_entry = disease_dict[defined_class_id]
            disease_entry['name'] = name
            disease_entry['description'] = description
            if tracker_item:
                disease_entry['tracker_item'] = tracker_item

def process_edges(mondo_data, omit_entities, age_onset_hierarchy, disease_dict, data_model):
    node_labels = {node['id']: node.get('lbl', 'Unknown') for node in mondo_data['graphs'][0]['nodes']}

    relationships_types = {}
    
    for record in mondo_data['graphs'][0]['edges']:
        subject_id = record.get('sub')
        property_id = record.get('pred')
        object_id = record.get('obj')

        if property_id == 'is_a' and subject_id in disease_dict and object_id in disease_dict:
            disease_dict[subject_id]['parent'] = object_id
            if 'children' not in disease_dict[object_id]:
                disease_dict[object_id]['children'] = []
            disease_dict[object_id]['children'].append(subject_id)

        if property_id in ['http://www.w3.org/2000/01/rdf-schema#subClassOf', 'subPropertyOf'] or object_id in omit_entities:
            continue

        if subject_id and property_id and object_id and 'MONDO' in subject_id:
            if subject_id in disease_dict:
                disease_entry = disease_dict[subject_id]
                relationship_type = "has_relationship"
                object_label = node_labels.get(object_id, 'Unknown')
                relationship_entry = create_relationship_entry(relationship_type, property_id, object_id, object_label)

                if 'MAXO' in object_id:
                    treatment_entry = {
                        "type": relationship_type,
                        "property": property_id,
                        "target": object_id,
                        "label": object_label
                    }
                    if treatment_entry not in disease_entry["treatments"]:
                        disease_entry["treatments"].append(treatment_entry)
                elif 'UBERON' in object_id:
                    anatomical_entry = {
                        "type": relationship_type,
                        "property": property_id,
                        "target": object_id,
                        "label": object_label
                    }
                    if anatomical_entry not in disease_entry["anatomical_structures"]:
                        disease_entry["anatomical_structures"].append(anatomical_entry)

                        if object_id not in data_model["anatomical_to_diseases"]:
                            data_model["anatomical_to_diseases"][object_id] = []
                        data_model["anatomical_to_diseases"][object_id].append(subject_id)

                    relationships_types[property_id] = "UBERON"

                elif 'HP' in object_id and object_id in age_onset_hierarchy:
                    age_onset_entry = {
                        "type": relationship_type,
                        "property": property_id,
                        "target": object_id,
                        "label": object_label
                    }
                    if age_onset_entry not in disease_entry["age_onsets"]:
                        disease_entry["age_onsets"].append(age_onset_entry)

                        if object_id not in data_model["age_onset_to_diseases"]:
                            data_model["age_onset_to_diseases"][object_id] = []
                        data_model["age_onset_to_diseases"][object_id].append(subject_id)
                    
                    relationships_types[property_id] = "HP"

                elif 'HP' in object_id:
                    phenotype_entry = {
                        "type": relationship_type,
                        "property": property_id,
                        "target": object_id,
                        "label": object_label
                    }
                    if phenotype_entry not in disease_entry["phenotypes"]:
                        disease_entry["phenotypes"].append(phenotype_entry)

                        if object_id not in data_model["phenotype_to_diseases"]:
                            data_model["phenotype_to_diseases"][object_id] = []
                        data_model["phenotype_to_diseases"][object_id].append(subject_id)
                    
                    relationships_types[property_id] = "HP"
    
    data_model["relationships_types"] = relationships_types


def finalize_data_model(disease_dict, data_model):
    for disease in disease_dict.values():
        if disease['treatments'] or disease['anatomical_structures'] or disease['phenotypes'] or disease['age_onsets']:
            if not disease['treatments']:
                del disease['treatments']
            if not disease['anatomical_structures']:
                del disease['anatomical_structures']
            if not disease['phenotypes']:
                del disease['phenotypes']
            if not disease['age_onsets']:
                del disease['age_onsets']
            data_model['diseases'].append(disease)

def save_to_mongodb(data_model, disease_dict, mongo_uri=config.MONGO_URI, db_name='mondo_db'):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    diseases_collection = db['diseases']
    data_model_collection = db['data_model']

    # Clear existing collections
    diseases_collection.delete_many({})
    data_model_collection.delete_many({})

    # Insert data
    diseases_collection.insert_many(disease_dict.values())
    data_model_collection.insert_one(data_model)

def train_model():
    
    fs = gridfs.GridFS(db.db)

    # Extraer datos de la colección de enfermedades
    diseases = list(db.get_diseases_collection())

    data_model = db.get_data_model()

    # Preparar los datos para el entrenamiento
    records = []

    relationships_types = data_model.get("relationships_types", {})

    # Convertir la estructura de datos en un formato adecuado
    for disease in diseases:
        disease_id = disease['id']
        disease_name = disease['name']

        for treatment in disease.get('treatments', []):
            records.append({
                'disease_id': disease_id,
                'disease_name': disease_name,
                'relationship_type': treatment['type'],
                'relationship_property': treatment['property'],
                'target_id': treatment['target']
            })
        for anatomical in disease.get('anatomical_structures', []):

            property_id = anatomical['property']
            target_id = anatomical['target']

            if property_id in relationships_types:
                if relationships_types[property_id] == "UBERON" and 'UBERON' not in target_id:
                    continue  # Saltar relaciones incorrectas
                if relationships_types[property_id] == "HP" and 'HP' not in target_id:
                    continue  # Saltar relaciones incorrectas

            records.append({
                'disease_id': disease_id,
                'disease_name': disease_name,
                'relationship_type': anatomical['type'],
                'relationship_property': anatomical['property'],
                'target_id': anatomical['target']
            })
        for phenotype in disease.get('phenotypes', []):


            property_id = phenotype['property']
            target_id = phenotype['target']

            if property_id in relationships_types:
                if relationships_types[property_id] == "UBERON" and 'UBERON' not in target_id:
                    continue  # Saltar relaciones incorrectas
                if relationships_types[property_id] == "HP" and 'HP' not in target_id:
                    continue  # Saltar relaciones incorrectas

            records.append({
                'disease_id': disease_id,
                'disease_name': disease_name,
                'relationship_type': phenotype['type'],
                'relationship_property': phenotype['property'],
                'target_id': phenotype['target']
            })
        for age_onset in disease.get('age_onsets', []):



            property_id = age_onset['property']
            target_id = age_onset['target']

            if property_id in relationships_types:
                if relationships_types[property_id] == "UBERON" and 'UBERON' not in target_id:
                    continue  # Saltar relaciones incorrectas
                if relationships_types[property_id] == "HP" and 'HP' not in target_id:
                    continue  # Saltar relaciones incorrectas

            records.append({
                'disease_id': disease_id,
                'disease_name': disease_name,
                'relationship_type': age_onset['type'],
                'relationship_property': age_onset['property'],
                'target_id': age_onset['target']
            })

    # Convertir los registros en un DataFrame
    df = pd.DataFrame(records)

    # Codificar datos categóricos
    le_disease = LabelEncoder()
    le_relationship_type = LabelEncoder()
    le_relationship_property = LabelEncoder()
    le_target_id = LabelEncoder()

    df['disease_id'] = le_disease.fit_transform(df['disease_id'])
    df['relationship_type'] = le_relationship_type.fit_transform(df['relationship_type'])
    df['relationship_property'] = le_relationship_property.fit_transform(df['relationship_property'])
    df['target_id'] = le_target_id.fit_transform(df['target_id'])

    # Ingeniería de características: crear características de interacción
    df['disease_rel_prop'] = df['disease_id'].astype(str) + '_' + df['relationship_property'].astype(str)
    le_disease_rel_prop = LabelEncoder()
    df['disease_rel_prop'] = le_disease_rel_prop.fit_transform(df['disease_rel_prop'])

    X = df[['disease_id', 'relationship_type', 'relationship_property', 'disease_rel_prop']]
    y = df['target_id']

    # Reducir el tamaño de los datos para el entrenamiento
    X_sample, _, y_sample, _ = train_test_split(X, y, train_size=0.1, random_state=42)

    # Dividir los datos reducidos en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X_sample, y_sample, test_size=0.2, random_state=42)

    # Manejar el desequilibrio de clases con RandomOverSampler
    ros = RandomOverSampler(random_state=42)
    X_train_res, y_train_res = ros.fit_resample(X_train, y_train)

    # Definir el modelo
    rf = RandomForestClassifier()

    # Definir una rejilla de hiperparámetros reducida
    param_dist = {
        'n_estimators': randint(10, 30),
        'max_depth': [10, 20, None],
        'min_samples_split': randint(2, 5),
        'min_samples_leaf': randint(1, 3),
        'bootstrap': [True]
    }

    # Usar RandomizedSearchCV con menos iteraciones y un solo trabajo
    random_search = RandomizedSearchCV(estimator=rf, param_distributions=param_dist, n_iter=10, cv=3, n_jobs=1, verbose=2, random_state=42)
    random_search.fit(X_train_res, y_train_res)

    # Obtener el mejor estimador
    best_rf = random_search.best_estimator_

    # Predecir en el conjunto de prueba
    y_pred = best_rf.predict(X_test)

    # Etiquetas únicas en y_test
    unique_labels = np.unique(y_test)

    # Evaluar el modelo
    accuracy = accuracy_score(y_test, y_pred)
    print(f'Accuracy: {accuracy}')
    print('Classification Report:')
    print(classification_report(y_test, y_pred, labels=unique_labels, target_names=le_target_id.inverse_transform(unique_labels)))

    # Guardar el modelo y los codificadores en MongoDB
    model_files = {
        'best_rf.pkl': best_rf,
        'le_disease.pkl': le_disease,
        'le_relationship_type.pkl': le_relationship_type,
        'le_relationship_property.pkl': le_relationship_property,
        'le_target_id.pkl': le_target_id,
        'le_disease_rel_prop.pkl': le_disease_rel_prop
    }

    # Guardar etiquetas vistas en un archivo JSON
    seen_labels = {
        'le_disease': le_disease.classes_.tolist(),
        'le_relationship_type': le_relationship_type.classes_.tolist(),
        'le_relationship_property': le_relationship_property.classes_.tolist(),
        'le_target_id': le_target_id.classes_.tolist(),
        'le_disease_rel_prop': le_disease_rel_prop.classes_.tolist()
    }

    for filename, model in model_files.items():
        with tempfile.NamedTemporaryFile() as temp_file:
            joblib.dump(model, temp_file.name)
            with open(temp_file.name, 'rb') as file_data:
                fs.put(file_data, filename=filename)
    
    # Guardar etiquetas vistas en MongoDB
    fs.put(json.dumps(seen_labels).encode('utf-8'), filename='seen_labels.json')

def main():
    mondo_data = load_mondo_data('datasets/mondo/mondo.json')

    omit_entities = {
        "http://purl.obolibrary.org/obo/MONDO_0000001",
        "http://purl.obolibrary.org/obo/HP_0000001",
        "http://purl.obolibrary.org/obo/MAXO_0000001",
        "http://purl.obolibrary.org/obo/UBERON_0000001"
    }

    age_onset_hierarchy = {
        "http://purl.obolibrary.org/obo/HP_0003674": "Onset"
    }

    data_model = {
        "diseases": [],
        "phenotype_to_diseases": {},
        "age_onset_to_diseases": {},
        "anatomical_to_diseases": {},
        "relationships_types": {}
    }

    disease_dict = {}

    # Build hierarchies
    is_a_hierarchy = build_is_a_hierarchy(mondo_data)
    onset_descendants = get_all_descendants("http://purl.obolibrary.org/obo/HP_0003674", is_a_hierarchy)
    for desc in onset_descendants:
        age_onset_hierarchy[desc] = "Onset"

    # Process data
    process_nodes(mondo_data, omit_entities, disease_dict)
    process_edges(mondo_data, omit_entities, age_onset_hierarchy, disease_dict, data_model)
    finalize_data_model(disease_dict, data_model)

    # Save to MongoDB
    save_to_mongodb(data_model, disease_dict)

    # train model
    train_model()

if __name__ == "__main__":
    main()
