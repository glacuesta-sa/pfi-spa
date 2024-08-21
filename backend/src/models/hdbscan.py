import repository
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

import matplotlib.pyplot as plt

from sklearn.cluster import HDBSCAN

# Function to add relationships to the data
def add_relationships(disease_data, disease, rel_type):
    disease_id = disease.get('id')
    name = disease.get('name')
    description = disease.get('description')
    for relationship in disease[rel_type]:  # phenotypes, anatomical_structures, chemicals, etc
        property_ = relationship.get('property')
        target = relationship.get('target')
        disease_data.append([disease_id, name, description, rel_type, property_, target])

def get_data_frame():
    data = repository.get_diseases()
    disease_data = []

    # relationships: phenotypes, chemicals, and anatomical_structures, etc
    for disease in data:
        if 'phenotypes' in disease:
            add_relationships(disease_data, disease, 'phenotypes')
        if 'chemicals' in disease:
            add_relationships(disease_data, disease, 'chemicals')
        if 'anatomical_structures' in disease:
            add_relationships(disease_data, disease, 'anatomical_structures')

    columns = ['Disease ID', 'Name', 'Description', 'Relationship Type', 'Property', 'Target']
    df = pd.DataFrame(disease_data, columns=columns)

    return df

def get_clustering_data_frame():
    df = get_data_frame()

    # Drop unnecessary columns
    df = df.drop(columns=['Description', 'Name'], errors='ignore')

    # Remove duplicates
    count_before = len(df)
    df = df.drop_duplicates()
    count_after = len(df)
    print(f"Count before removing duplicates: {count_before}")
    print(f"Count after removing duplicates: {count_after}")

    # Check for missing values
    missing_values = df.isnull().sum()
    print("Missing values per column:")
    print(missing_values)

    # Drop rows with any missing values
    df = df.dropna()

    # One-hot encode columns
    df = pd.get_dummies(df, columns=['Relationship Type'], prefix='RelType')

    # Select features for clustering
    features = ['Disease ID', 'Property', 'Target', 'RelType_anatomical_structures', 'RelType_chemicals', 'RelType_phenotypes']

    # Encode categorical features
    df['Disease ID'] = df['Disease ID'].astype('category').cat.codes
    df['Property'] = df['Property'].astype('category').cat.codes
    df['Target'] = df['Target'].astype('category').cat.codes

    # Scale the features
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df[features])

    # apply HDBSCAN
    min_cluster_size = 25 
    hdbscan_clusterer = HDBSCAN(min_cluster_size=min_cluster_size, metric='manhattan')
    clusters = hdbscan_clusterer.fit_predict(scaled_features)

    df['Cluster'] = clusters

    # number of clusters and noise points
    n_clusters = len(set(clusters)) - (1 if -1 in clusters else 0)
    n_noise = list(clusters).count(-1)

    print(f'Number of clusters: {n_clusters}')
    print(f'Number of noise points: {n_noise}')

    sil_score = silhouette_score(scaled_features, clusters)
    print(f'Silhouette Score: {sil_score:.2f}')
    # TODO save outputs to .jpg file in output folder

    return df