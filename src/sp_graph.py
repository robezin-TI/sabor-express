import os
import osmnx as ox

CACHE_PATH = os.path.join("data", "sp_drive.graphml")

def get_sp_graph(force_reload: bool = False):
    """
    Baixa (ou carrega do cache) o grafo viário 'drive' de São Paulo (município).
    Retorna um MultiDiGraph pronto para roteamento.
    """
    os.makedirs("data", exist_ok=True)
    if os.path.exists(CACHE_PATH) and not force_reload:
        return ox.load_graphml(CACHE_PATH)

    # Você pode trocar para um polígono maior (ex.: "São Paulo, Brazil" já é bem grande).
    # Para RMSP, pode usar "São Paulo, São Paulo, Brazil" (município) + limites maiores.
    G = ox.graph_from_place("São Paulo, Brazil", network_type="drive", simplify=True)
    G = ox.add_edge_speeds(G)      # vel. km/h estimada (OSM)
    G = ox.add_edge_travel_times(G)  # tempo (segundos) a partir da vel. e comprimento
    ox.save_graphml(G, CACHE_PATH)
    return G
