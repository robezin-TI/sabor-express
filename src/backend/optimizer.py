from math import radians, cos, sin, asin, sqrt
from itertools import permutations
import networkx as nx
import osmnx as ox

def _haversine_km(a, b):
    lat1, lon1 = a
    lat2, lon2 = b
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    x = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return 2 * R * asin(sqrt(x))

def _center_and_radius(points):
    lat = sum(p[0] for p in points)/len(points)
    lon = sum(p[1] for p in points)/len(points)
    r = max(_haversine_km((lat, lon), p) for p in points) * 1000.0  # em m
    return (lat, lon), r

def _astar_heuristic(G, u, v):
    # heurística: distância em linha reta entre nós (em metros)
    uy, ux = G.nodes[u]["y"], G.nodes[u]["x"]
    vy, vx = G.nodes[v]["y"], G.nodes[v]["x"]
    return _haversine_km((uy, ux), (vy, vx)) * 1000.0

def _pairwise_cost_matrix(G, nodes, points):
    """Custo A* (metros) entre todos os pares de nós."""
    n = len(nodes)
    cost = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j: 
                continue
            try:
                d = nx.astar_path_length(
                    G, nodes[i], nodes[j],
                    heuristic=lambda u, v: _astar_heuristic(G, u, v),
                    weight="length"
                )
            except Exception:
                # fallback: haversine em metros
                d = _haversine_km(points[i], points[j]) * 1000.0
            cost[i][j] = d
    return cost

def _nearest_neighbor(cost):
    n = len(cost)
    unvisited = set(range(1, n))
    path = [0]
    cur = 0
    while unvisited:
        nxt = min(unvisited, key=lambda j: cost[cur][j])
        unvisited.remove(nxt)
        path.append(nxt)
        cur = nxt
    return path

def _two_opt(order, cost):
    """Melhora a rota com 2-opt."""
    n = len(order)
    improved = True
    while improved:
        improved = False
        for i in range(1, n-2):
            for k in range(i+1, n-1):
                a, b = order[i-1], order[i]
                c, d = order[k], order[k+1]
                old = cost[a][b] + cost[c][d]
                new = cost[a][c] + cost[b][d]
                if new + 1e-6 < old:
                    order[i:k+1] = reversed(order[i:k+1])
                    improved = True
    return order

def optimize_routes(points, speed_kmh=30.0):
    """
    points: [(lat, lon), ...]
    Retorna:
      - route_coords: lista [ [lat,lon], ... ] polilinha completa pelas ruas
      - order_idx: ordem dos índices dos pontos originais
      - dist_km: distância total
      - eta_min: tempo estimado
    """
    if len(points) < 2:
        return [list(points[0])], [0], 0.0, 0.0

    center, radius_m = _center_and_radius(points)
    # margem extra para garantir cobertura do grafo
    G = ox.graph_from_point(center, dist=max(1500.0, radius_m + 1000.0), network_type="drive")

    # mapear cada ponto ao nó do grafo mais próximo
    nodes = [ox.distance.nearest_nodes(G, X=p[1], Y=p[0]) for p in points]

    # custo entre todos os pares via A*
    cost = _pairwise_cost_matrix(G, nodes, points)

    # TSP heurístico: vizinho mais próximo + 2-opt
    order = _nearest_neighbor(cost)
    order.append(order[0])  # volta ao início? (para entrega geralmente não precisa)
    # Se NÃO quiser retorno ao início, remova a linha acima e ajuste 2-opt se desejar.
    order = _two_opt(order, cost)

    # construir polilinha pelas ruas com A*
    full_nodes = []
    total_m = 0.0
    for i in range(len(order)-1):
        u = nodes[order[i]]
        v = nodes[order[i+1]]
        try:
            path = nx.astar_path(
                G, u, v,
                heuristic=lambda a, b: _astar_heuristic(G, a, b),
                weight="length"
            )
            full_nodes += path if not full_nodes else path[1:]
            seg_m = nx.path_weight(G, path, weight="length")
            total_m += seg_m
        except Exception:
            # fallback: segmento em linha reta (raro)
            full_nodes += [u, v]
            total_m += _haversine_km(points[order[i]], points[order[i+1]]) * 1000.0

    route_coords = [[G.nodes[n]["y"], G.nodes[n]["x"]] for n in full_nodes]

    dist_km = round(total_m/1000.0, 3)
    eta_min = round((dist_km / max(1e-6, speed_kmh)) * 60.0, 1)

    # ordem dos pontos (sem o retorno ao início na lista final)
    order_idx = order[:-1]

    return route_coords, order_idx, dist_km, eta_min
