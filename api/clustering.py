from sklearn.cluster import KMeans
import numpy as np

def kmeans_clusters(points, k=2, random_state=42):
    """
    points: [{"lat":..,"lon":..}, ...]
    retorna: {"labels":[...], "centroids":[{"lat":..,"lon":..}, ...]}
    """
    if not points:
        return {"labels": [], "centroids": []}
    X = np.array([[p["lat"], p["lon"]] for p in points], dtype=float)
    k = max(1, min(k, len(points)))
    km = KMeans(n_clusters=k, n_init="auto", random_state=random_state)
    labels = km.fit_predict(X).tolist()
    cents = [{"lat": float(c[0]), "lon": float(c[1])} for c in km.cluster_centers_]
    return {"labels": labels, "centroids": cents}
