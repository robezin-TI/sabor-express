from sklearn.cluster import KMeans
import numpy as np

def cluster_points(points, n_clusters=3):
    """
    points: lista de dicionários [{'lat': float, 'lng': float}, ...]
    """
    X = np.array([[p["lat"], p["lng"]] for p in points])
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)

    clustered = []
    for i, point in enumerate(points):
        clustered.append({
            "lat": point["lat"],
            "lng": point["lng"],
            "cluster": int(labels[i])
        })
    return clustered, kmeans.cluster_centers_.tolist()
