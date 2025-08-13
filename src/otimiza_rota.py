import networkx as nx
from math import radians, sin, cos, asin

def _haversine_km(a, b):
    R = 6371.0
    lat1, lon1 = a
    lat2, lon2 = b
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    return 2 * R * asin((sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2)**0.5)

def _heuristica_factory(G, destino, peso="tempo_min", vel_padrao_kmh=40.0):
    def h(u, _):
        try:
            a = (G.nodes[u]["latitude"], G.nodes[u]["longitude"])
            b = (G.nodes[destino]["latitude"], G.nodes[destino]["longitude"])
            dist = _haversine_km(a, b)
            return (dist / vel_padrao_kmh * 60.0) if peso == "tempo_min" else dist
        except KeyError:
            return 0.0
    return h

def menor_caminho_astar(G, origem, destino, peso="tempo_min"):
    h = _heuristica_factory(G, destino, peso)
    caminho = nx.astar_path(G, origem, destino, heuristic=h, weight=peso)
    custo = nx.path_weight(G, caminho, weight=peso)
    return caminho, custo

def ordenar_paradas_vizinho_mais_proximo(G, origem, paradas, peso="tempo_min"):
    restantes = set(paradas)
    ordem, atual = [], origem
    while restantes:
        melhor, melhor_custo = None, float("inf")
        for p in list(restantes):
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

def rota_com_paradas(G, origem, paradas, destino, peso="tempo_min", ordenar=True):
    if ordenar and paradas:
        paradas = ordenar_paradas_vizinho_mais_proximo(G, origem, paradas, peso)

    caminho_total, custo_total = [origem], 0.0
    atual = origem
    for alvo in list(paradas) + [destino]:
        h = _heuristica_factory(G, alvo, peso)
        seg = nx.astar_path(G, atual, alvo, heuristic=h, weight=peso)
        custo_total += nx.path_weight(G, seg, weight=peso)
        caminho_total += seg[1:]  # evita duplicar o nó atual
        atual = alvo
    return caminho_total, custo_total
