from typing import List, Tuple
import networkx as nx
import osmnx as ox
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pandas as pd

def geocode_many(enderecos: List[str]) -> List[Tuple[float, float, str]]:
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
    out = []
    for lat, lon, label in pontos_latlon:
        nid = ox.distance.nearest_nodes(G, lon, lat)  # x=lon, y=lat
        out.append((nid, label, lat, lon))
    return out

def _heuristica(G, destino, peso):
    def h(u, _):
        ax, ay = G.nodes[u]["x"], G.nodes[u]["y"]
        bx, by = G.nodes[destino]["x"], G.nodes[destino]["y"]
        d = ox.distance.great_circle_vec(ay, ax, by, bx)  # metros
        if peso == "length":
            return d
        # travel_time -> segundos (aprox 50 km/h = 13.9 m/s)
        return d / 13.9
    return h

def astar_path(G, u, v, peso="travel_time"):
    h = _heuristica(G, v, peso)
    path = nx.astar_path(G, u, v, heuristic=h, weight=peso)
    custo = nx.path_weight(G, path, weight=peso)
    return path, custo

def order_stops_nearest_neighbor(G, origem, paradas, peso="travel_time"):
    restantes = list(paradas)
    ordem, atual = [], origem
    while restantes:
        melhor, best = None, float("inf")
        for p in restantes:
            try:
                c = nx.shortest_path_length(G, atual, p, weight=peso)
            except nx.NetworkXNoPath:
                c = float("inf")
            if c < best:
                melhor, best = p, c
        ordem.append(melhor)
        restantes.remove(melhor)
        atual = melhor
    return ordem

def route_with_stops(G, origem, paradas, destino, peso="travel_time", ordenar=True):
    if ordenar and paradas:
        paradas = order_stops_nearest_neighbor(G, origem, paradas, peso)
    seq = [origem] + paradas + [destino]
    caminho_total, custo_total = [], 0.0
    for i in range(len(seq)-1):
        seg, custo = astar_path(G, seq[i], seq[i+1], peso=peso)
        if i > 0:
            seg = seg[1:]
        caminho_total += seg
        custo_total += custo
    return caminho_total, custo_total, seq

def route_summary(G, caminho_nodes):
    # travel_time está em segundos e length em metros nas edges
    tempos = ox.utils_graph.get_route_edge_attributes(G, caminho_nodes, "travel_time")
    dists = ox.utils_graph.get_route_edge_attributes(G, caminho_nodes, "length")
    tempo_min = sum(tempos) / 60.0 if tempos else 0.0
    dist_km = sum(dists) / 1000.0 if dists else 0.0

    legs = []
    for i in range(len(caminho_nodes)-1):
        u, v = caminho_nodes[i], caminho_nodes[i+1]
        edge = G[u][v][0] if isinstance(G[u][v], dict) else G[u][v]
        tempo = edge.get("travel_time", 0) / 60.0
        dist = edge.get("length", 0) / 1000.0
        legs.append({
            "De": f"{G.nodes[u].get('y'):.5f}, {G.nodes[u].get('x'):.5f}",
            "Para": f"{G.nodes[v].get('y'):.5f}, {G.nodes[v].get('x'):.5f}",
            "Distância (km)": round(dist, 3),
            "Tempo (min)": round(tempo, 1),
        })
    return tempo_min, dist_km, pd.DataFrame(legs)
