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
            "eta_min": 0.0
        }

    # calcula centro para baixar grafo
    lat_center = sum(p["lat"] for p in points) / len(points)
    lon_center = sum(p["lon"] for p in points) / len(points)

    # baixa grafo de direção (ruas) ao redor do centro
    G = ox.graph_from_point((lat_center, lon_center), dist=graph_dist_m, network_type="drive")

    # mapeia pontos aos nós mais próximos
    nodes = []
    for p in points:
        try:
            n = nearest_node(G, p["lat"], p["lon"])
        except Exception:
            # fallback: node None (pode acontecer em áreas sem cobertura)
            n = None
        nodes.append(n)

    # define ordem (heurística TSP: nearest neighbor)
    order_idx = tsp_nearest_neighbor(points)

    # percorre par-a-par calculando caminho mais curto via A* (weight = length)
    full_nodes = []
    total_m = 0.0
    for i in range(len(order_idx) - 1):
        a_idx = order_idx[i]
        b_idx = order_idx[i + 1]
        u = nodes[a_idx]
        v = nodes[b_idx]

        # se algum nó for None ou igual, use fallback euclidiano
        if u is None or v is None or u == v:
            # aproximação: adiciona linha reta entre as coordenadas
            # não adicionamos nós do grafo, apenas incrementamos distância haversine
            total_m += haversine_km(
                (points[a_idx]["lat"], points[a_idx]["lon"]),
                (points[b_idx]["lat"], points[b_idx]["lon"])
            ) * 1000.0
            # append both endpoints as coords (mantendo custo mínimo)
            full_nodes.append((points[a_idx]["lat"], points[a_idx]["lon"]))
            full_nodes.append((points[b_idx]["lat"], points[b_idx]["lon"]))
            continue

        try:
            path = nx.astar_path(
                G, u, v,
                heuristic=lambda x, y: haversine_km(
                    (G.nodes[x]["y"], G.nodes[x]["x"]),
                    (G.nodes[y]["y"], G.nodes[y]["x"])
                ) * 1000.0,
                weight="length"
            )
            # evita duplicar o nó inicial quando concatenar
            if not full_nodes:
                # converte todos
                full_nodes.extend([(G.nodes[n]["y"], G.nodes[n]["x"]) for n in path])
            else:
                # pula primeiro nó
                full_nodes.extend([(G.nodes[n]["y"], G.nodes[n]["x"]) for n in path][1:])

            seg_m = nx.path_weight(G, path, weight="length")
            total_m += seg_m
        except Exception:
            # fallback para caminho direto (linha reta) quando A* falha
            total_m += haversine_km(
                (points[a_idx]["lat"], points[a_idx]["lon"]),
                (points[b_idx]["lat"], points[b_idx]["lon"])
            ) * 1000.0
            full_nodes.append((points[a_idx]["lat"], points[a_idx]["lon"]))
            full_nodes.append((points[b_idx]["lat"], points[b_idx]["lon"]))

    # compacta route coords (remove sequências duplicadas consecutivas)
    route_coords = []
    for latlon in full_nodes:
        if not route_coords or (round(route_coords[-1][0], 6), round(route_coords[-1][1], 6)) != (round(latlon[0], 6), round(latlon[1], 6)):
            route_coords.append([latlon[0], latlon[1]])

    dist_km = round(total_m / 1000.0, 3)
    eta_min = round((dist_km / max(speed_kmh, 1e-6)) * 60.0, 1)

    ordered_points = [points[i] for i in order_idx]

    return {
        "ordered_points": ordered_points,
        "route": route_coords,
        "distance_km": dist_km,
        "eta_min": eta_min
    }
