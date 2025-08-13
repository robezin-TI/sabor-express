import pandas as pd
from sklearn.cluster import KMeans

def agrupar_entregas(df, n_clusters=2, random_state=42):
    """df precisa conter colunas: latitude, longitude."""
    if not {"latitude", "longitude"}.issubset(df.columns):
        raise ValueError("df precisa ter colunas 'latitude' e 'longitude'")
    coords = df[["latitude", "longitude"]]
    kmeans = KMeans(n_clusters=n_clusters, n_init="auto", random_state=random_state)
    df = df.copy()
    df["cluster"] = kmeans.fit_predict(coords)
    return df, kmeans
