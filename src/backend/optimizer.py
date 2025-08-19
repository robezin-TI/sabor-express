from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import numpy as np
import requests
from sklearn.cluster import KMeans

OSRM_BASE = "http://router.project-osrm.org"  # pode trocar por seu servidor OSRM

@dataclass
class Point:
    id: str
    lat: float
    lon: float
    addr: str = ""

def to_np(points: List[Point]) -> np.ndarray:
    return np.array([[p.lat, p.lon] for p in points], dtype=float)

def kmeans_clusters(points: List[Point], k: int) -> Dict[int, List[Point]]:
    if k <= 0 or k > len(points):
        k = max(1, int(np.sqrt(len(points))))  # heurística simples
    X = to_np(points)
    model = KMeans(n_clusters=k, n_init="auto", random_state=42)
    labels = model.fit_predict(X)
    clusters: Dict[int, List[Point]] = {}
    for lbl, p in zip(labels, points):
        clusters.setdefault(int(lbl), []).append(p)
    return clusters

# --------- OSRM helpers ---------
def _coord_str(points: List[Point]) -> str:
    # OSRM exige "lon,lat"
    return ";".join(f"{p.lon:.6f},{p.lat:.6f}" for p in points)

def osrm_table(points: List[Point]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Retorna (distance_m, duration_s) como matrizes NxN usando OSRM /table.
    """
    if len(points) == 1:
        return np.zeros((1,1)), np.zeros((1,1))
    coords = _coord_str(points)
    url = f"{OSRM_BASE}/table/v1/driving/{coords}"
    params = {"annotations": "distance,duration"}
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    dist = np.array(data["distances"], dtype=float)  # metros
    dur = np.array(data["durations"], dtype=float)   # segundos
    # pode vir None quando OSRM não consegue conectar pontos (raro em áreas mapeadas)
    dist = np.nan_to_num(dist, nan=1e9)
    dur = np.nan_to_num(dur, nan=1e9)
    return dist, dur

def osrm_route_geometry(points_ordered: List[Point]) -> Tuple[List[List[float]], float, float]:
    """
    Chama /route para a sequência final e retorna:
      - geometry: lista [[lat, lon], ...]
      - distance_km (float)
      - duration_min (float)
    """
    if len(points_ordered) == 1:
        p = points_ordered[0]
        return [[p.lat, p.lon]], 0.0, 0.0
    coords = _coord_str(points_ordered)
    url = f"{OSRM_BASE}/route/v1/driving/{coords}"
    params = {"overview": "full", "geometries": "geojson", "steps": "false"}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    route = data["routes"][0]
    geom = route["geometry"]["coordinates"]  # [lon, lat]
    # converter para [lat, lon] p/ Leaflet
    latlon = [[xy[1], xy[0]] for xy in geom]
    distance_km = float(route["distance"]) / 1000.0
    duration_min = float(route["duration"]) / 60.0
    return latlon, distance_km, duration_min

# --------- TSP (usa a MATRIZ DE DURAÇÃO do OSRM) ---------
def tsp_with_2opt_by_duration(points: List[Point], start_idx: int = 0) -> Tuple[List[int], float, float]:
    """
    Resolve TSP simples:
      - vizinho mais próximo usando DURATIONS (s)
      - melhoria 2-opt
    Retorna (ordem_indices, total_distance_km, total_duration_min)
    """
    n = len(points)
    if n <= 1:
        return list(range(n)), 0.0, 0.0

    Dm, Tm = osrm_table(points)   # metros, segundos

    # vizinho mais próximo minimizando duração
    unvisited = set(range(n))
    route = [start_idx]
    unvisited.remove(start_idx)
    while unvisited:
        last = route[-1]
        nxt = min(unvisited, key=lambda j: Tm[last, j])
        route.append(nxt)
        unvisited.remove(nxt)

    # 2-opt por duração
    def cost(rt: List[int]) -> float:
        return sum(Tm[rt[i], rt[i+1]] for i in range(len(rt)-1))

    best = route[:]
    best_c = cost(best)
    improved = True
    while improved:
        improved = False
        for i in range(1, n - 2):
            for j in range(i + 1, n - 1):
                new_rt = best[:i] + best[i:j+1][::-1] + best[j+1:]
                new_c = cost(new_rt)
                if new_c + 1e-6 < best_c:
                    best, best_c = new_rt, new_c
                    improved = True
                    break
            if improved:
                break

    # somatórios reais a partir das matrizes
    total_m = sum(Dm[best[i], best[i+1]] for i in range(n-1))
    total_s = sum(Tm[best[i], best[i+1]] for i in range(n-1))
    return best, total_m/1000.0, total_s/60.0

# --------- Função principal ---------
def optimize(points: List[Point], k_clusters: Optional[int] = None) -> Dict:
    clusters = kmeans_clusters(points, k_clusters or 0)

    result = {"clusters": [], "total_km": 0.0, "total_eta_min": 0.0}
    for label, pts in clusters.items():
        # ponto inicial = heurística simples: o mais "sudoeste" (ou poderia ser depósito)
        start_idx = int(np.argmin([ (p.lat, p.lon) for p in pts ]))

        order_idx, length_km, eta_min = tsp_with_2opt_by_duration(pts, start_idx=start_idx)
        ordered = [pts[i] for i in order_idx]

        # rota final com geometria para desenhar nas ruas
        geometry, route_km, route_min = osrm_route_geometry(ordered)

        result["clusters"].append({
            "label": int(label),
            "order": [p.id for p in ordered],
            "points": [{"id": p.id, "lat": p.lat, "lon": p.lon, "addr": p.addr} for p in ordered],
            "distance_km": round(route_km, 3),
            "eta_min": round(route_min, 1),
            "geometry": geometry  # lista [[lat,lon], ...]
        })
        result["total_km"] += route_km
        result["total_eta_min"] += route_min

    result["total_km"] = round(result["total_km"], 3)
    result["total_eta_min"] = round(result["total_eta_min"], 1)
    return result
