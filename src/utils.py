import pandas as pd
import networkx as nx
from math import radians, sin, cos, asin

def haversine_km(lat1, lon1, lat2, lon2):
    """Distância geodésica em KM."""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * asin(a**0.5)
    return R * c

def carregar_locais_csv(caminho):
    # colunas esperadas: id,name,latitude,longitude
    return pd.read_csv(caminho)

def carregar_arestas_csv(caminho):
    # colunas esperadas: origem_id,destino_id,via,dist_km,velocidade_kmh
    return pd.read_csv(caminho)

def construir_grafo(locais_csv, arestas_csv, usar_tempo=True, velocidade_padrao_kmh=35):
    """Monta o grafo a partir dos CSVs e calcula pesos (tempo_min e dist_km)."""
    locais = carregar_locais_csv(locais_csv)
    arestas = carregar_arestas_csv(arestas_csv)

    G = nx.Graph()
    # nós
    for _, r in locais.iterrows():
        G.add_node(
            r["id"],
            name=r.get("name", r["id"]),
            latitude=float(r["latitude"]),
            longitude=float(r["longitude"]),
        )

    # arestas
    for _, r in arestas.iterrows():
        u, v = r["origem_id"], r["destino_id"]
        vel = float(r.get("velocidade_kmh", velocidade_padrao_kmh))
        dist = r.get("dist_km", None)
        if pd.isna(dist) or float(dist) == 0:
            a, b = G.nodes[u], G.nodes[v]
            dist = haversine_km(a["latitude"], a["longitude"], b["latitude"], b["longitude"])
        dist = float(dist)
        tempo_min = (dist / vel) * 60.0

        G.add_edge(u, v,
                   via=r.get("via", ""),
                   dist_km=dist,
                   tempo_min=tempo_min)

    # peso padrão para operações do networkx
    for _, _, d in G.edges(data=True):
        d["weight"] = d["tempo_min"] if usar_tempo else d["dist_km"]
    return G

def imprimir_resumo_rota(G, caminho, peso="tempo_min"):
    """Imprime passos, distância e tempo da rota."""
    total = 0.0
    print("➡️  Passo a passo:")
    for i in range(len(caminho) - 1):
        u, v = caminho[i], caminho[i + 1]
        dados = G[u][v]
        custo = dados[peso]
        total += custo
        print(f"  {i+1}. {G.nodes[u]['name']} → {G.nodes[v]['name']} "
              f"({dados['dist_km']:.2f} km | {dados['tempo_min']:.1f} min)")
    unidade = "min" if peso == "tempo_min" else "km"
    print(f"✅ Custo total ({peso}): {total:.2f} {unidade}")
    return total
