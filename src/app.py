import streamlit as st
from streamlit_folium import st_folium
import folium
from routing import geocode_many, nearest_nodes, route_with_stops, route_summary
from graph_sp import get_sp_graph
import osmnx as ox
import os

st.set_page_config(page_title="Rota Inteligente - São Paulo", layout="wide")

st.title("🗺️ Rota Inteligente (São Paulo)")
st.caption("Digite origem, paradas (uma por linha) e destino. O app otimiza a ordem das paradas e calcula a rota com A* no grafo viário real de São Paulo (OpenStreetMap).")

with st.sidebar:
    st.header("Parâmetros")
    origem = st.text_input("Origem", value="Itapecerica Shopping, Itapecerica da Serra, SP")
    paradas_txt = st.text_area("Paradas (uma por linha)", value="McDonald's, Av. Elias Yazbek, Embu das Artes, SP")
    destino = st.text_input("Destino", value="Shopping Taboão, Taboão da Serra, SP")
    criterio = st.radio("Otimizar por", ["Tempo (recomendado)", "Distância"], index=0)
    ordenar = st.checkbox("Otimizar ordem das paradas (TSP heurístico)", value=True)
    btn = st.button("Gerar rota")

st.info("Dica: você pode colar vários endereços reais. O mapa cobre **toda a cidade de São Paulo** (grafo de direção).", icon="ℹ️")

if btn:
    try:
        st.write("⏳ Preparando grafo viário de São Paulo...")
        G = get_sp_graph()

        st.write("📍 Geocodificando endereços...")
        enderecos = [origem] + [e for e in paradas_txt.splitlines() if e.strip()] + [destino]
        geos = geocode_many(enderecos)
        nos = nearest_nodes(G, geos)

        origem_id = nos[0][0]
        destino_id = nos[-1][0]
        paradas_ids = [n[0] for n in nos[1:-1]]
        labels = {nid: label for (nid, label, _, _) in nos}

        peso = "travel_time" if "Tempo" in criterio else "length"
        st.write("🧭 Calculando rota ótima com A*...")
        caminho, custo, sequencia = route_with_stops(
            G, origem_id, paradas_ids, destino_id, peso=peso, ordenar=ordenar
        )

        # métricas
        tempo_min, dist_km, legs = route_summary(G, caminho)
        col1, col2, col3 = st.columns(3)
        col1.metric("Tempo estimado", f"{tempo_min:.1f} min")
        col2.metric("Distância total", f"{dist_km:.1f} km")
        col3.metric("Segmentos", f"{len(legs)} trechos")

        # mapa
        st.write("🗺️ Mapa da rota")
        n0 = caminho[0]
        m = folium.Map(location=[G.nodes[n0]["y"], G.nodes[n0]["x"]], zoom_start=11, control_scale=True)

        latlon = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in caminho]
        folium.PolyLine(latlon, weight=7, opacity=0.8).add_to(m)

        # marcadores
        for idx, n in enumerate(caminho):
            lbl = labels.get(n, f"Ponto {idx+1}")
            if n == caminho[0]:
                icon = folium.Icon(color="green", icon="play")
            elif n == caminho[-1]:
                icon = folium.Icon(color="red", icon="flag")
            else:
                icon = folium.Icon(color="blue", icon="circle")
            folium.Marker([G.nodes[n]["y"], G.nodes[n]["x"]], tooltip=lbl, popup=lbl, icon=icon).add_to(m)

        st_folium(m, width=None, height=600)

        # tabela de passos
        st.write("🧾 Passo a passo da rota")
        st.dataframe(legs, use_container_width=True)

        # exportar HTML
        os.makedirs("outputs", exist_ok=True)
        out_html = "outputs/rota.html"
        m.save(out_html)
        st.success(f"Mapa exportado: {out_html}")

    except Exception as e:
        st.error(f"Erro: {e}")
else:
    st.write("➡️ Preencha os endereços na barra lateral e clique em **Gerar rota**.")
