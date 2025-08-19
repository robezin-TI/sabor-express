import requests
import numpy as np
from sklearn.cluster import KMeans
import sys
import json

class Point:
    def __init__(self, id, lat, lon, addr=""):
        self.id = id
        self.lat = float(lat)
        self.lon = float(lon)
        self.addr = addr

# -----------------------------
# Distâncias reais via OSRM
# -----------------------------
def osrm_table(points):
    coords = ";".join([f"{p.lon},{p.lat}" for p in points])
    url = f"http://router.project-osrm.org/table/v1/driving/{coords}"
    params = {"annotations": "distance,duration"}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        dist = np.array(data["distances"])
        dur = np.array(data["durations"])
        return dist, dur
    except Exception as e:
        print("OSRM error:", e, file=sys.stderr, flush=True)
        # fallback → matriz grande para forçar outro caminho
        n = len(points)
        return np.ones((n, n)) * 1e6, np.ones((n, n)) * 1e6

def osrm_route_geometry(points_ordered):
    coords = ";".join([f"{p.lon},{p.lat}" for p in points_ordered])
    url = f"http://router.project-osrm.org/route/v1/driving/{coords}"
    params = {"overview": "full", "geometries": "geojson"}
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        route = data["routes"][0]
        geom = route["geometry"]["coordinates"]
        return geom, route["distance"] / 1000.0, route["duration"] / 60.0
    except Exception as e:
        print("OSRM route error:", e, file=sys.stderr, flush=True)
        # fallback → linhas retas
        return [[p.lon, p.lat] for p in points_ordered], 0.0, 0.0

# -----------------------------
# Heurística TSP
# -----------------------------
def tsp_nearest(dist_matrix):
    n = len(dist_matrix)
    if n == 0: return []
    visited = [False] * n
    order = [0]
    visited[0] = True
    for _ in range(n - 1):
        last = order[-1]
        next_city = np.argmin([
            dist_matrix[last][j] if not visited[j] else np.inf
            for j in range(n)
        ])
        order.append(next_city)
        visited[next_city] = True
    return order

# -----------------------------
# Otimizador principal
# -----------------------------
def optimize(points, k=None):
    if len(points) < 2:
        return {"error": "Forneça pelo menos 2 pontos"}

    X = np.array([[p.lat, p.lon] for p in points])

    # define k clusters
    if not k or k <= 0:
        k = 1
    elif k > len(points):
        k = len(points)

    # clustering
    kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
    labels = kmeans.fit_predict(X)

    clusters = []
    total_km = 0
    total_eta = 0

    for cluster_id in range(k):
        cluster_pts = [p for i, p in enumerate(points) if labels[i] == cluster_id]

        if len(cluster_pts) < 2:
            clusters.append({"id": cluster_id, "points": cluster_pts, "order": [0]})
            continue

        # matriz de distâncias
        dist, dur = osrm_table(cluster_pts)

        # ordem ótima (TSP)
        order = tsp_nearest(dist)

        ordered_pts = [cluster_pts[i] for i in order]

        # rota real
        geom, dist_km, eta_min = osrm_route_geometry(ordered_pts)

        clusters.append({
            "id": cluster_id,
            "points": [vars(p) for p in ordered_pts],
            "order": order,
            "geometry": geom
        })

        total_km += dist_km
        total_eta += eta_min

    result = {
        "clusters": clusters,
        "total_km": round(total_km, 3),
        "total_eta_min": round(total_eta, 1)
    }

    print("DEBUG result:", json.dumps(result)[:500], file=sys.stderr, flush=True)
    return result
