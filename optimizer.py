import networkx as nx
import osmnx as ox


def optimize_routes(points):
    if len(points) < 2:
        return [], points

    # Criar grafo da região ao redor do primeiro ponto
    lat0, lon0 = points[0]["lat"], points[0]["lon"]
    G = ox.graph_from_point((lat0, lon0), dist=5000, network_type="drive")

    ordered_points = []
    route_coords = []

    current = points[0]
    ordered_points.append(current)

    for next_point in points[1:]:
        orig = ox.distance.nearest_nodes(G, current["lon"], current["lat"])
        dest = ox.distance.nearest_nodes(G, next_point["lon"], next_point["lat"])

        try:
            path = nx.astar_path(G, orig, dest, weight="length")
            coords = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in path]
            route_coords.extend(coords)
        except nx.NetworkXNoPath:
            pass

        ordered_points.append(next_point)
        current = next_point

    return route_coords, ordered_points
