import networkx as nx
import osmnx as ox

ox.settings.log_console = False
ox.settings.use_cache = True

def optimize_routes(points):
    """Calcula rota ótima com A* entre os pontos fornecidos"""
    if len(points) < 2:
        return [], 0, 0

    # monta grafo
    center = (points[0]["lat"], points[0]["lon"])
    G = ox.graph_from_point(center, dist=5000, network_type="drive")

    route = []
    total_dist = 0
    total_time = 0

    for i in range(len(points) - 1):
        orig = ox.distance.nearest_nodes(G, points[i]["lon"], points[i]["lat"])
        dest = ox.distance.nearest_nodes(G, points[i + 1]["lon"], points[i + 1]["lat"])

        path = nx.astar_path(G, orig, dest, weight="length")
        dist = sum(ox.utils_graph.get_route_edge_attributes(G, path, "length"))
        time = dist / (40 * 1000 / 60)  # velocidade média 40km/h

        route.extend(path)
        total_dist += dist
        total_time += time

    return route, round(total_dist / 1000, 2), round(total_time, 2)
