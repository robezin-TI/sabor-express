from typing import List, Tuple
import networkx as nx
import folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import osmnx as ox

def geocode_many(enderecos: List[str]) -> List[Tuple[float, float, str]]:
    """
    Geocodifica endereços em (lat, lon, label). Usa Nominatim (OSM).
    """
    geolocator = Nominatim(user_agent="rota-inteligente-sp")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    coords = []
    for e in enderecos:
        r = geocode(e)
        if r is None:
            raise ValueError(f"Endereço não encontrado: {e}")
        coords.append((r.latitude, r.longitude, e))
    return coords

def nearest_nodes(G, pontos_latlon: List[Tuple[float, float, str]]):
    """
    Para cada ponto (lat, lon, label), retorna o node id mais próximo.
    """
    nodes = []
    for lat, lon, label in pontos_latlon:
        nid = ox.distance.nearest_nodes(G, lon, lat)  # atenção: (x=lon, y=lat)
        nodes.append((nid, label, lat, lon))
    return nodes

def astar_path(G, u, v, peso="travel_time"):
    """
    A* sobre o grafo OSMnx; heurística euclidiana na malha viária.
    peso: 'travel_time' (segundos) ou 'length' (metros).
    """
    # OSMnx armazena nós com atributos 'x' (lon) e 'y' (lat)
    def h_func(a, b):
        ax, ay = G.nodes[a]["x"], G.nodes[a]["y"]
        bx, by = G.nodes[b]["x"], G.nodes[b]["y"]
        return ox.distance.great_circle_vec(ay, ax, by, bx) if peso == "length" else \
               ox.distance.great_circle_vec(ay, ax, by, bx) / 13.9  # aprox 50 km/h -> m/s

    path = nx.astar_path(G, u, v, heuristic=h_func, weight=peso)
    custo = nx.path_weight(G, path, weight=peso)
    return path, custo

def order_stops_nearest_neighbor(G, origem, paradas, peso="travel_time"):
    restantes = list(paradas)
    ordem, atual = [], origem
    while restantes:
        melhor, melhor_custo = None, float("inf")
        for p in restantes:
            try:
                c = nx.shortest_path_length(G, atual, p, weight=peso)
            except nx.NetworkXNoPath:
                c = float("inf")
            if c < melhor_custo:
                melhor, melhor_custo = p, c
        ordem.append(melhor)
        restantes.remove(melhor)
        atual = melhor
    return ordem

def route_with_stops(G, origem, paradas, destino, peso="travel_time", ordenar=True):
    if ordenar and paradas:
        paradas = order_stops_nearest_neighbor(G, origem, paradas, peso)
    sequencia = [origem] + paradas + [destino]
    caminho_total, custo_total = [], 0.0
    for i in range(len(sequencia)-1):
        seg, custo = astar_path(G, sequencia[i], sequencia[i+1], peso=peso)
        if i > 0:  # evita duplicar nó
            seg = seg[1:]
        caminho_total += seg
        custo_total += custo
    return caminho_total, custo_total, sequencia

def render_map(G, caminho_nodes, labels_por_node, out_html="outputs/rota.html"):
    os.makedirs(os.path.dirname(out_html), exist_ok=True)
    # centro no primeiro nó
    n0 = caminho_nodes[0]
    m = folium.Map(location=[G.nodes[n0]["y"], G.nodes[n0]["x"]], zoom_start=11, control_scale=True)

    # polyline
    latlon = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in caminho_nodes]
    folium.PolyLine(latlon, weight=6, opacity=0.7).add_to(m)

    # marcadores (origem/paradas/destino)
    primeiro, ultimo = caminho_nodes[0], caminho_nodes[-1]
    for idx, n in enumerate([primeiro] + caminho_nodes[1:-1] + [ultimo]):
        txt = labels_por_node.get(n, f"Ponto {idx+1}")
        icon = "play" if n == primeiro else ("flag" if n == ultimo else "cloud")
        folium.Marker([G.nodes[n]["y"], G.nodes[n]["x"]], popup=txt, tooltip=txt,
                      icon=folium.Icon(icon=icon)).add_to(m)
    m.save(out_html)
    return out_html
