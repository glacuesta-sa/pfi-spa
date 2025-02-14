import time

import utils
import services
import psutil

import repository
import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_score, train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report
from imblearn.over_sampling import RandomOverSampler
from scipy.stats import randint


def generate_model(df_with_clusters, include_cluster):
    """
    Generate a RandomForest model using previously generated collections of diseases and data models,
    and save the trained model and associated encoders to MongoDB.

    Hyperparameters:
    - n_estimators: Number of trees in the forest. Randomly chosen between 10 and 30. High number of n_estimators complexizes the model, giving better accuracy but reduced performance.
    - max_depth: Maximum depth of the trees. Chosen from [10, 20, None]. Maximum depth of the tree will be 10, 20 or None. Nodes are expanded until all leaves are pure or until they contain fewer than min_samples_split samples.
    - min_samples_split: Minimum number of samples required to split an internal node. Randomly chosen between 2 and 4.
    - min_samples_leaf: Minimum number of samples required to be at a leaf node. Randomly chosen between 1 and 2.
    """
    print(f"random forest")
    print(f"ENTRENANDO MODELO, ESTO PUEDE TOMAR UNOS MINUTOS.")
    print(f"ENTRENANDO MODELO, ESTO PUEDE TOMAR UNOS MINUTOS.")
    print(f"ENTRENANDO MODELO, ESTO PUEDE TOMAR UNOS MINUTOS.")
    print(f"ENTRENANDO MODELO, ESTO PUEDE TOMAR UNOS MINUTOS.")
    print(f"ENTRENANDO MODELO, ESTO PUEDE TOMAR UNOS MINUTOS.")
    print(f"ENTRENANDO MODELO, ESTO PUEDE TOMAR UNOS MINUTOS.")
    print(f"ENTRENANDO MODELO, ESTO PUEDE TOMAR UNOS MINUTOS.")
    print(f"ENTRENANDO MODELO, ESTO PUEDE TOMAR UNOS MINUTOS.")
    print(f"ENTRENANDO MODELO, ESTO PUEDE TOMAR UNOS MINUTOS.")
    print(f"ENTRENANDO MODELO, ESTO PUEDE TOMAR UNOS MINUTOS.")
    print(f"ENTRENANDO MODELO, ESTO PUEDE TOMAR UNOS MINUTOS.")
    print(f"ENTRENANDO MODELO, ESTO PUEDE TOMAR UNOS MINUTOS.")
    print(f"ENTRENANDO MODELO, ESTO PUEDE TOMAR UNOS MINUTOS.")
    print(f"ENTRENANDO MODELO, ESTO PUEDE TOMAR UNOS MINUTOS.")
    df = get_data_frame()

    # encode to string
    df['disease_id'] = df['disease_id'].astype(str)
    df['relationship_property'] = df['relationship_property'].astype(str)
    df['target_id'] = df['target_id'].astype(str)

    if include_cluster:
        df_with_clusters['Disease ID'] = df_with_clusters['Disease ID'].astype(str)
        df_with_clusters['Property'] = df_with_clusters['Property'].astype(str)
        df_with_clusters['Target'] = df_with_clusters['Target'].astype(str)
        # merge dataframe with clustered dataframe
        df = pd.merge(df, df_with_clusters[['Disease ID', 'Property', 'Target', 'Cluster']],
                    left_on=['disease_id', 'relationship_property', 'target_id'],
                    right_on=['Disease ID', 'Property', 'Target'],
                    how='left')

        # Drop unnecessary columns after merge
        df.drop(columns=['Disease ID', 'Property', 'Target'], inplace=True)
        
    print(f"random forest 2")
    # categorical features (disease_id, relationship_property, target_id) are encoded using LabelEncoder.
    le_disease = LabelEncoder()
    le_relationship_type = LabelEncoder()
    le_relationship_property = LabelEncoder()
    le_target_id = LabelEncoder()

    df['disease_id'] = le_disease.fit_transform(df['disease_id'])
    df['relationship_type'] = le_relationship_type.fit_transform(df['relationship_type'])
    df['relationship_property'] = le_relationship_property.fit_transform(df['relationship_property'])
    df['target_id'] = le_target_id.fit_transform(df['target_id'])
    
    print(f"random forest 3")
    # Ingeniería de características: crear características de interacción
    df['disease_rel_prop'] = df['disease_id'].astype(str) + '_' + df['relationship_property'].astype(str)
    le_disease_rel_prop = LabelEncoder()
    df['disease_rel_prop'] = le_disease_rel_prop.fit_transform(df['disease_rel_prop'])
    
    print(f"random forest 4")
    # TODO disease_age_onset

    X = df[['disease_id', 'relationship_type', 'relationship_property', 'disease_rel_prop']]

    if include_cluster:
        le_cluster = LabelEncoder()
        df['Cluster'] = le_cluster.fit_transform(df['Cluster'].fillna(-1))  # fillna for potential NaNs
        X['Cluster'] = df['Cluster']


    y = df['target_id']

    #print(df['disease_id'].value_counts())
    #print(df['relationship_property'].value_counts())
    #print(df['target_id'].value_counts())

    # reduce train set
    #X_sample, _, y_sample, _ = train_test_split(X, y, train_size=0.1, random_state=42)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    print(f"random forest 5")
    
    # data augmentation
    ros = RandomOverSampler(random_state=42)
    X_train_res, y_train_res = ros.fit_resample(X_train, y_train)

    # define RandomForest model
    rf = RandomForestClassifier()

    # hyper parameters definition
    param_dist = {
        'n_estimators': randint(10, 30),
        'max_depth': [10, 20, None],
        'min_samples_split': randint(2, 5),
        'min_samples_leaf': randint(1, 3),
    }

    # cross validation sets
    cv = 10
    print(f"random forest 6 - entrenando modelos, esto va a tomar unos minutos.")
    # pefromance tracking
    start_time = time.time()
    process = psutil.Process()

    # RandomizedSearchCV parameters, less iterators single worker
    random_search = RandomizedSearchCV(estimator=rf, param_distributions=param_dist, n_iter=10, cv=cv, n_jobs=1, verbose=0, random_state=42)
    random_search.fit(X_train_res, y_train_res)
    print(f"random forest 7")
    
    # get RandomForest best indicator
    best_rf = random_search.best_estimator_

    # predict in X test subset
    y_pred = best_rf.predict(X_test)
    
    print(f"random forest 8")
    
    # unique labels in test subset
    unique_labels = np.unique(y_test)

    # performance metrics
    elapsed_time = time.time() - start_time
    memory_usage = process.memory_info().rss / (1024 * 1024)  # convert to MB

    print(f"Elapsed Time: {elapsed_time:.2f} seconds")
    print(f"Memory Usage: {memory_usage:.2f} MB")

    # evaluate model TODO needs improvement
    accuracy = accuracy_score(y_test, y_pred)
    print(f'Accuracy: {accuracy}')
    print(f"random forest 9")
    
    # cross validation
    cross_val_scores = cross_val_score(best_rf, X_train_res, y_train_res, cv=cv, scoring='accuracy', error_score='raise')
    print(f"Cross-Validation Score (mean): {cross_val_scores.mean():.4f}")
    print(f"Cross-Validation Score (std): {cross_val_scores.std():.4f}")
    print(f"random forest 10")

    #print('Classification Report:')
    #print(classification_report(y_test, y_pred, labels=unique_labels, target_names=le_target_id.inverse_transform(unique_labels)))
    # TODO save outputs to .jpg file in output folder


    if not include_cluster:
        # save random_forest model to MongoDB
        model_files = {
            'best_rf.pkl': best_rf,
            'le_disease.pkl': le_disease,
            'le_relationship_type.pkl': le_relationship_type,
            'le_relationship_property.pkl': le_relationship_property,
            'le_target_id.pkl': le_target_id,
            'le_disease_rel_prop.pkl': le_disease_rel_prop
        }

        # seen labels
        seen_labels = {
        'le_disease': le_disease.classes_.tolist(),
        'le_relationship_type': le_relationship_type.classes_.tolist(),
        'le_relationship_property': le_relationship_property.classes_.tolist(),
        'le_target_id': le_target_id.classes_.tolist(),
        'le_disease_rel_prop': le_disease_rel_prop.classes_.tolist()
        }
        print(f"random forest 11")
        for filename, model in model_files.items():
            utils.upload_to_datalake(filename, model)
    
        # save seen labels to mongoDB FS
        #repository.fs.put(json.dumps(seen_labels).encode('utf-8'), filename='seen_labels.json')



def get_data_frame(): 
    print(f"get dataframe")
    # get data structures previously generated collections
    diseases = repository.get_diseases()

    records = []
    for disease in diseases:
        disease_id = disease['id']
        disease_name = disease['name']
    
        # treatment relationships  
        for treatment in disease.get('treatments', []):

            property_id = treatment['property']
            target_id = treatment['target']

            if not services.is_valid_relationship(property_id, target_id):
                continue

            records.append({
                'disease_id': disease_id,
                'disease_name': disease_name,
                'relationship_type': treatment['type'],
                'relationship_property': treatment['property'],
                'target_id': treatment['target']
            })

        # anatomical relationships
        for anatomical in disease.get('anatomical_structures', []):

            property_id = anatomical['property']
            target_id = anatomical['target']

            if not services.is_valid_relationship(property_id, target_id):
                continue

            records.append({
                'disease_id': disease_id,
                'disease_name': disease_name,
                'relationship_type': anatomical['type'],
                'relationship_property': anatomical['property'],
                'target_id': anatomical['target']
            })

        # phenotypic relationships
        for phenotype in disease.get('phenotypes', []):

            property_id = phenotype['property']
            target_id = phenotype['target']

            if not services.is_valid_relationship(property_id, target_id):
                continue

            records.append({
                'disease_id': disease_id,
                'disease_name': disease_name,
                'relationship_type': phenotype['type'],
                'relationship_property': phenotype['property'],
                'target_id': phenotype['target']
            })

        # age onset relationships
        for age_onset in disease.get('age_onsets', []):

            property_id = age_onset['property']
            target_id = age_onset['target']

            if not services.is_valid_relationship(property_id, target_id):
                continue

            records.append({
                'disease_id': disease_id,
                'disease_name': disease_name,
                'relationship_type': age_onset['type'],
                'relationship_property': age_onset['property'],
                'target_id': age_onset['target']
            })

        # exposure relationships
        for exposure in disease.get('exposures', []):

            property_id = exposure['property']
            target_id = exposure['target']

            if not services.is_valid_relationship(property_id, target_id):
                continue

            records.append({
                'disease_id': disease_id,
                'disease_name': disease_name,
                'relationship_type': exposure['type'],
                'relationship_property': exposure['property'],
                'target_id': exposure['target']
            })

        # chemical relationships
        for chemical in disease.get('chemicals', []):

            property_id = chemical['property']
            target_id = chemical['target']

            if not services.is_valid_relationship(property_id, target_id):
                continue

            records.append({
                'disease_id': disease_id,
                'disease_name': disease_name,
                'relationship_type': chemical['type'],
                'relationship_property': chemical['property'],
                'target_id': chemical['target']
            })

    df = pd.DataFrame(records)
    print(f"reached end of get dataframe")
    return df