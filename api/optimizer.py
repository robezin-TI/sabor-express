import math
import networkx as nx
import osmnx as ox

ox.settings.log_console = False
ox.settings.use_cache = True

def _centroid(points):
    lat = sum(p["lat"] for p in points)/len(points)
    lon = sum(p["lon"] for p in points)/len(points)
    return (lat, lon)

def optimize_routes(points):
    """
    Calcula rota entre os pontos na ordem fornecida usando A* no grafo viário OSM.
    Retorna (node_path, distancia_km, tempo_min)
    """
    if len(points) < 2:
        return [], 0.0, 0.0

    center = _centroid(points)
    # raio em metros (ajuste conforme necessidade)
    G = ox.graph_from_point(center, dist=7000, network_type="drive")

    route_nodes = []
    total_m = 0.0

    for i in range(len(points)-1):
        o = points[i]
        d = points[i+1]
        orig = ox.distance.nearest_nodes(G, o["lon"], o["lat"])
        dest = ox.distance.nearest_nodes(G, d["lon"], d["lat"])
        path = nx.astar_path(
            G, orig, dest,
            heuristic=lambda u, v: 0,  # fica equivalente a Dijkstra com peso 'length'
            weight="length"
        )
        # Distância da etapa
        edge_lengths = ox.utils_graph.get_route_edge_attributes(G, path, "length")
        stage = sum(edge_lengths)
        total_m += stage

        if route_nodes and path and route_nodes[-1] == path[0]:
            route_nodes.extend(path[1:])
        else:
            route_nodes.extend(path)

    # velocidade média 40 km/h
    tempo_min = total_m / (40_000/60)
    return route_nodes, round(total_m/1000, 2), round(tempo_min, 2)
