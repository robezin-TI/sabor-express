import os
import osmnx as ox

CACHE_PATH = os.path.join("data", "sp_drive.graphml")

def get_sp_graph(force_reload: bool = False):
    """
    Carrega o grafo viário 'drive' de São Paulo (município).
    Na 1ª execução baixa do OpenStreetMap, calcula velocidades/tempos e salva em cache.
    """
    os.makedirs("data", exist_ok=True)
    if os.path.exists(CACHE_PATH) and not force_reload:
        return ox.load_graphml(CACHE_PATH)

    G = ox.graph_from_place("São Paulo, Brazil", network_type="drive", simplify=True)
    G = ox.add_edge_speeds(G)         # km/h
    G = ox.add_edge_travel_times(G)   # segundos
    ox.save_graphml(G, CACHE_PATH)
    return G
