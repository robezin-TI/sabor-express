from sklearn.cluster import KMeans

def cluster_deliveries(points, k=2):
    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    model.fit(points)
    labels = model.labels_.tolist()
    centers = model.cluster_centers_.tolist()
    return {"labels": labels, "centers": centers}
