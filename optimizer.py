import networkx as nx
import osmnx as ox
from math import radians, cos, sin, asin, sqrt

# Config moderno do OSMnx (1.9.x)
ox.settings.use_cache = True
ox.settings.log_console = False

def _haversine_km(a, b):
    lat1, lon1 = a
    lat2, lon2 = b
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    x = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return 2 * R * asin(sqrt(x))

def _nearest_neighbor_order(points):
    # heurística simples p/ TSP: começa no 1º e vai ao mais próximo
    n = len(points)
    if n <= 2:
        return list(range(n))
    unused = set(range(1, n))
    order = [0]
    while unused:
        last = order[-1]
        nxt = min(unused, key=lambda j: _haversine_km(points[last], points[j]))
        order.append(nxt)
        unused.remove(nxt)
    return order

def _astar_geo_heuristic(G, u, v):
    # heurística A*: distância em linha reta entre nós do grafo
    uy, ux = G.nodes[u]['y'], G.nodes[u]['x']
    vy, vx = G.nodes[v]['y'], G.nodes[v]['x']
    return _haversine_km((uy, ux), (vy, vx)) * 1000.0  # metros

def optimize_routes(points, speed_kmh=30.0, dist_m=4000):
    """
    points: [(lat, lon), ...]
    Retorna: (route_coords, ordered_idx, dist_km, eta_min)
    """
    # Centro para baixar o grafo
    center = (sum(p[0] for p in points)/len(points),
              sum(p[1] for p in points)/len(points))

    # Grafo viário (somente vias dirigíveis)
    G = ox.graph_from_point(center, dist=dist_m, network_type="drive")

    # Mapeia cada ponto ao nó mais próximo
    nodes = [ox.distance.nearest_nodes(G, X=p[1], Y=p[0]) for p in points]

    # Define ordem dos pontos (TSP guloso) — cumpre requisito acadêmico
    order = _nearest_neighbor_order(points)

    # Percorre par a par calculando menor caminho por A*
    full_nodes = []
    total_m = 0.0
    for i in range(len(order)-1):
        u = nodes[order[i]]
        v = nodes[order[i+1]]
        path = nx.astar_path(G, u, v, heuristic=lambda x, y: _astar_geo_heuristic(G, x, y), weight="length")
        # concatena evitando repetir o nó anterior
        full_nodes += path if not full_nodes else path[1:]
        total_m += nx.path_weight(G, path, weight="length")

    # Converte nós para coordenadas [lat, lon]
    route_coords = [[G.nodes[n]["y"], G.nodes[n]["x"]] for n in full_nodes]

    dist_km = round(total_m/1000.0, 3)
    eta_min = round((dist_km / max(speed_kmh, 1e-6)) * 60.0, 1)

    return route_coords, order, dist_km, eta_min
