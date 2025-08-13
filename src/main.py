from utils import construir_grafo, imprimir_resumo_rota
from otimiza_rota import rota_com_paradas

if __name__ == "__main__":
    # monta o grafo a partir dos CSVs
    G = construir_grafo("data/locais.csv", "data/arestas.csv", usar_tempo=True)

    origem = "ITA_SHOP"
    paradas = ["MCD_EMBU"]  # você pode adicionar mais IDs aqui
    destino = "TAB_SHOP"

    print("\n=== ROTA OTIMIZADA PELO TEMPO (A*) ===")
    caminho, _ = rota_com_paradas(G, origem, paradas, destino, peso="tempo_min", ordenar=True)
    print(" → ".join(G.nodes[n]["name"] for n in caminho))
    imprimir_resumo_rota(G, caminho, peso="tempo_min")

    print("\n=== ROTA OTIMIZADA PELA DISTÂNCIA (A*) ===")
    caminho_km, _ = rota_com_paradas(G, origem, paradas, destino, peso="dist_km", ordenar=True)
    print(" → ".join(G.nodes[n]["name"] for n in caminho_km))
    imprimir_resumo_rota(G, caminho_km, peso="dist_km")
