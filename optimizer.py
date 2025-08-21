import networkx as nx
import osmnx as ox
from math import radians, cos, sin, asin, sqrt

def _haversine_km(a, b):
    lat1, lon1 = a
    lat2, lon2 = b
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    x = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return 2 * R * asin(sqrt(x))

def optimize_routes(points, speed_kmh=30.0):
    center = (sum(p[0] for p in points)/len(points),
              sum(p[1] for p in points)/len(points))

    G = ox.graph_from_point(center, dist=2000, network_type="drive")
    nodes = [ox.distance.nearest_nodes(G, X=p[1], Y=p[0]) for p in points]

    order = list(range(len(points)))  # ordem simples (pode ser TSP se quiser)

    full_nodes = []
    total_m = 0.0
    for i in range(len(order)-1):
        u = nodes[order[i]]
        v = nodes[order[i+1]]
        path = nx.shortest_path(G, u, v, weight="length", method="dijkstra")
        full_nodes += path if not full_nodes else path[1:]
        total_m += nx.path_weight(G, path, weight="length")

    route_coords = [[G.nodes[n]["y"], G.nodes[n]["x"]] for n in full_nodes]
    dist_km = round(total_m/1000.0, 3)
    eta_min = round((dist_km / max(speed_kmh, 1e-6)) * 60.0, 1)

    return route_coords, order, dist_km, eta_min
