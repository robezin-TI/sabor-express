import math
from typing import List, Tuple, Dict
import networkx as nx
import osmnx as ox

# configurações básicas do osmnx (segundo a sua versão)
ox.settings.use_cache = True
ox.settings.log_console = False

def haversine_km(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    # a=(lat,lon) b=(lat,lon)
    R = 6371.0
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(h))


def nearest_node(G, lat: float, lon: float):
    # OSMnx usa ordem (x=lon, y=lat)
    return ox.distance.nearest_nodes(G, lon, lat)


def tsp_nearest_neighbor(points: List[Dict]) -> List[int]:
    """
    Retorna uma ordem de visita (índices) usando vizinho mais próximo,
    fixando o primeiro ponto como partida (sem retorno ao início).
    points: lista de dicts com 'lat' e 'lon'
    """
    n = len(points)
    if n <= 2:
        return list(range(n))
    unvisited = set(range(1, n))
    route = [0]
    current = 0
    while unvisited:
        best = min(unvisited, key=lambda j: haversine_km(
            (points[current]["lat"], points[current]["lon"]),
            (points[j]["lat"], points[j]["lon"])
        ))
        route.append(best)
        unvisited.remove(best)
        current = best
    return route


def optimize_routes(points: List[Dict], speed_kmh: float = 30.0, graph_dist_m: int = 4000) -> Dict:
    """
    points: [{'lat': float, 'lon': float, 'label': str}, ...]
    Retorna dicionário com:
      - ordered_points: lista de pontos reordenados (mesma estrutura)
      - route: lista de [lat, lon] representando a polilinha completa nas ruas
      - distance_km: distância total aproximada (km)
      - eta_min: tempo estimado total (min)
    """
    if not isinstance(points, list) or len(points) < 2:
        return {
            "ordered_points": points,
            "route": [],
            "distance_km": 0.0,
            "

