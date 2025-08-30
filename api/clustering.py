from sklearn.cluster import KMeans
import numpy as np

def cluster_points(points, n_clusters=2):
    """Aplica KMeans nos pontos (lat, lon)."""
    if len(points) < n_clusters:
        n_clusters = len(points)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(points)
    return labels, kmeans.cluster_centers_
