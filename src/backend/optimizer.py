import networkx as nx
import osmnx as ox
from itertools import permutations

def haversine_distance(p1, p2):
    """Distância aproximada entre dois pontos (lat, lon)."""
    from math import radians, cos, sin, asin, sqrt
    lat1, lon1 = p1
    lat2, lon2 = p2
    R = 6371  # km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return 2 * R * asin(sqrt(a))

def optimize_routes(points):
    """
    Otimiza rota usando menor caminho entre pontos via OSMnx + NetworkX.
    """
    if len(points) < 2:
        return points, 0, 0

    # baixar grafo da região
    lat, lon = points[0]
    G = ox.graph_from_point((lat, lon), dist=5000, network_type="drive")

    # converter pontos para nós no grafo
    nodes = [ox.distance.nearest_nodes(G, lon, lat) for lat, lon in points]

    # calcular rota ótima (força bruta para poucos pontos)
    best_order = None
    best_dist = float("inf")
    for perm in permutations(nodes):
        dist = 0
        for i in range(len(perm)-1):
            try:
                path_len = nx.shortest_path_length(G, perm[i], perm[i+1], weight="length")
                dist += path_len
            except Exception:
                dist += haversine_distance(points[i], points[i+1]) * 1000
        if dist < best_dist:
            best_dist = dist
            best_order = perm

    # converter nós de volta para coordenadas
    route = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in best_order]

    # tempo estimado: 40km/h
    eta_min = (best_dist/1000) / 40 * 60

    return route, round(best_dist/1000, 3), round(eta_min, 1)
