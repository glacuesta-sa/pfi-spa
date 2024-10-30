import time
import psutil
import services
import repository

import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_score, train_test_split
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import StratifiedKFold

from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import RandomOverSampler


def generate_model(df_with_clusters, include_cluster):
    """
    Generate an XGBoost model using previously generated collections of diseases and data models,
    and save the trained model and associated encoders to MongoDB.
    """

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

    # Encode to string
    df['disease_id'] = df['disease_id'].astype(str)
    df['relationship_property'] = df['relationship_property'].astype(str)
    df['target_id'] = df['target_id'].astype(str)

    if include_cluster:
        df_with_clusters['Disease ID'] = df_with_clusters['Disease ID'].astype(str)
        df_with_clusters['Property'] = df_with_clusters['Property'].astype(str)
        df_with_clusters['Target'] = df_with_clusters['Target'].astype(str)
        # Merge dataframe with clustered dataframe
        df = pd.merge(df, df_with_clusters[['Disease ID', 'Property', 'Target', 'Cluster']],
                      left_on=['disease_id', 'relationship_property', 'target_id'],
                      right_on=['Disease ID', 'Property', 'Target'],
                      how='left')

        # Drop unnecessary columns after merge
        df.drop(columns=['Disease ID', 'Property', 'Target'], inplace=True)

    # Categorical features (disease_id, relationship_property, target_id) are encoded using LabelEncoder.
    le_disease = LabelEncoder()
    le_relationship_type = LabelEncoder()
    le_relationship_property = LabelEncoder()
    le_target_id = LabelEncoder()
    

    df['disease_id'] = le_disease.fit_transform(df['disease_id'])
    df['relationship_type'] = le_relationship_type.fit_transform(df['relationship_type'])
    df['relationship_property'] = le_relationship_property.fit_transform(df['relationship_property'])
    df['target_id'] = le_target_id.fit_transform(df['target_id'])

    # Feature engineering: create interaction features
    df['disease_rel_prop'] = df['disease_id'].astype(str) + '_' + df['relationship_property'].astype(str)
    le_disease_rel_prop = LabelEncoder()
    df['disease_rel_prop'] = le_disease_rel_prop.fit_transform(df['disease_rel_prop'])

    # TODO disease_age_onset

    X = df[['disease_id', 'relationship_type', 'relationship_property', 'disease_rel_prop']]

    if include_cluster:
        le_cluster = LabelEncoder()
        df['Cluster'] = le_cluster.fit_transform(df['Cluster'].fillna(-1))  # fillna for potential NaNs
        X['Cluster'] = df['Cluster']

    y = df['target_id']
    y = le_target_id.fit_transform(y)

    # data augmentation for minority clases
    #smote = SMOTE(k_neighbors=1)
    #X_resampled, y_resampled = smote.fit_resample(X, y)
    ros = RandomOverSampler(random_state=42)
    X_resampled, y_resampled = ros.fit_resample(X, y)

    # data reduction for majority classes
    #rus = RandomUnderSampler()
    #X_resampled, y_resampled = rus.fit_resample(X, y)

    X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.3, random_state=42)

    # ensure seen labels
    y_train = le_target_id.fit_transform(y_train)
    y_test = safe_transform(le_target_id, y_test)

    # pefromance tracking
    start_time = time.time()
    process = psutil.Process()

    # Define the XGBoost model
    xgb = XGBClassifier(n_estimators=50, max_depth=3, learning_rate=0.1, eval_metric='mlogloss', verbosity=0)
    xgb.fit(X_train, y_train)

    # cross validation scores
    cross_val_scores = cross_val_score(xgb, X_resampled, y_resampled, cv=3, scoring='accuracy', error_score='raise')
    print(f"Cross-Validation Score (mean): {cross_val_scores.mean():.4f}")
    print(f"Cross-Validation Score (std): {cross_val_scores.std():.4f}")
    
    # predict
    y_pred = xgb.predict(X_test)

    # performance metrics
    elapsed_time = time.time() - start_time
    memory_usage = process.memory_info().rss / (1024 * 1024)  # convert to MB

    print(f"Elapsed Time: {elapsed_time:.2f} seconds")
    print(f"Memory Usage: {memory_usage:.2f} MB")

    # Evaluate model
    accuracy = accuracy_score(y_test, y_pred)
    print(f'Accuracy: {accuracy}')
    # TODO save outputs to .jpg file in output folder

def get_data_frame():
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
    return df

def safe_transform(encoder, y):
    """ Safely transform y by handling unseen labels """
    try:
        return encoder.transform(y)
    except ValueError as e:
        seen_classes = set(encoder.classes_)
        y_transformed = []
        for label in y:
            if label in seen_classes:
                y_transformed.append(encoder.transform([label])[0])
            else:
                y_transformed.append(-1)
        return np.array(y_transformed)