import networkx as nx
import osmnx as ox

def _nearest_node(G, lat, lon):
    # osmnx usa ordem (x=lon, y=lat)
    return ox.distance.nearest_nodes(G, lon, lat)

def optimize_routes(points):
    """
    Recebe: [{"lat": ..., "lon": ..., "label": ...}, ...]
    Faz A* entre os pontos na ordem atual (você pode reordenar manualmente no UI
    e/ou clicar em 'Otimizar rota' para recalcular o traçado nas RUAS).
    Retorna: (route_coords, ordered_points)
      - route_coords: [(lat, lon), ...] para desenhar a polilinha
      - ordered_points: mesma sequência de pontos (aqui mantemos a ordem enviada)
    """
    if len(points) < 2:
        return [], points

    # Grafo de ruas ao redor do primeiro ponto (5 km)
    lat0, lon0 = float(points[0]["lat"]), float(points[0]["lon"])
    G = ox.graph_from_point((lat0, lon0), dist=5000, network_type="drive")

    route_coords = []
    ordered_points = list(points)

    # A* entre pares consecutivos
    for i in range(len(ordered_points) - 1):
        a = ordered_points[i]
        b = ordered_points[i + 1]

        orig = _nearest_node(G, float(a["lat"]), float(a["lon"]))
        dest = _nearest_node(G, float(b["lat"]), float(b["lon"]))

        # A* ponderando por distância (edge attribute 'length' em metros)
        path = nx.astar_path(G, orig, dest, weight="length")
        coords = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in path]
        # evita duplicar o nó inicial quando concatena segmentos
        if route_coords and coords:
            coords = coords[1:]
        route_coords.extend(coords)

    return route_coords, ordered_points
