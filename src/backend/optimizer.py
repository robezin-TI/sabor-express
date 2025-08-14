from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import numpy as np
from sklearn.cluster import KMeans
from .geo import haversine_km

@dataclass
class Point:
    id: str
    lat: float
    lon: float

def to_np(points: List[Point]) -> np.ndarray:
    return np.array([[p.lat, p.lon] for p in points], dtype=float)

def kmeans_clusters(points: List[Point], k: int) -> Dict[int, List[Point]]:
    if k <= 0 or k > len(points):
        k = max(1, int(np.sqrt(len(points))))  # heurística simples
    X = to_np(points)
    model = KMeans(n_clusters=k, n_init="auto", random_state=42)
    labels = model.fit_predict(X)
    clusters: Dict[int, List[Point]] = {}
    for label, p in zip(labels, points):
        clusters.setdefault(int(label), []).append(p)
    return clusters

# matriz de distâncias haversine
def distance_matrix(points: List[Point]) -> np.ndarray:
    n = len(points)
    M = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(i + 1, n):
            d = haversine_km((points[i].lat, points[i].lon), (points[j].lat, points[j].lon))
            M[i, j] = M[j, i] = d
    return M

# heurística TSP: nearest neighbor + 2-opt
def tsp_route(points: List[Point], start_idx: int = 0) -> Tuple[List[int], float]:
    n = len(points)
    if n <= 1:
        return list(range(n)), 0.0
    M = distance_matrix(points)

    # nearest neighbor
    unvisited = set(range(n))
    route = [start_idx]
    unvisited.remove(start_idx)
    while unvisited:
        last = route[-1]
        nxt = min(unvisited, key=lambda j: M[last, j])
        route.append(nxt)
        unvisited.remove(nxt)

    # 2-opt improvement
    improved = True
    def total_len(rt: List[int]) -> float:
        return sum(M[rt[i], rt[i+1]] for i in range(len(rt)-1))
    best_len = total_len(route)
    while improved:
        improved = False
        for i in range(1, n - 2):
            for j in range(i + 1, n - 1):
                new_route = route[:i] + route[i:j+1][::-1] + route[j+1:]
                new_len = total_len(new_route)
                if new_len + 1e-9 < best_len:
                    route = new_route
                    best_len = new_len
                    improved = True
                    break
            if improved:
                break

    return route, best_len

def estimate_eta_km(distance_km: float, avg_speed_kmh: float = 25.0) -> float:
    """retorna ETA em minutos (aprox). velocidade média de motoboy ~25km/h intra-urbano."""
    return (distance_km / max(1e-6, avg_speed_kmh)) * 60.0

def optimize(points: List[Point], k_clusters: Optional[int] = None) -> Dict:
    # clusterização (ML)
    clusters = kmeans_clusters(points, k_clusters or 0)

    result = {"clusters": [], "total_km": 0.0, "total_eta_min": 0.0}
    for label, pts in clusters.items():
        # escolhe início como o mais ao sul-oeste (heurística simples)
        start_idx = int(np.argmin([ (p.lat, p.lon) for p in pts ]))
        order_idx, length_km = tsp_route(pts, start_idx=start_idx)
        ordered = [pts[i] for i in order_idx]
        eta_min = estimate_eta_km(length_km)

        result["clusters"].append({
            "label": int(label),
            "order": [p.id for p in ordered],
            "points": [{"id": p.id, "lat": p.lat, "lon": p.lon} for p in ordered],
            "distance_km": round(length_km, 3),
            "eta_min": round(eta_min, 1)
        })
        result["total_km"] += length_km
        result["total_eta_min"] += eta_min

    result["total_km"] = round(result["total_km"], 3)
    result["total_eta_min"] = round(result["total_eta_min"], 1)
    return result

