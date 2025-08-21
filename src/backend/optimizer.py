import networkx as nx
import osmnx as ox
from sklearn.cluster import KMeans

# carregar grafo viário de Itapecerica da Serra
print("📍 Carregando grafo viário...")
G = ox.graph_from_place("Itapecerica da Serra, São Paulo, Brasil", network_type="drive")

def shortest_path(a, b):
    """Menor caminho entre dois pontos usando A*"""
    orig = ox.distance.nearest_nodes(G, a[1], a[0])
    dest = ox.distance.nearest_nodes(G, b[1], b[0])
    path = nx.astar_path(G, orig, dest, weight="length")
    edges = [(G.nodes[n]["x"], G.nodes[n]["y"]) for n in path]
    return edges

def optimize(addresses, clusters=1):
    coords = [a["coords"] for a in addresses]
    if not coords:
        return {"error": "Nenhum ponto fornecido."}

    # clustering opcional
    labels = [0] * len(coords)
    if clusters > 1 and len(coords) >= clusters:
        kmeans = KMeans(n_clusters=clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(coords)

    routes, total_distance, total_eta = [], 0.0, 0.0

    for cluster_id in set(labels):
        cluster_points = [coords[i] for i, l in enumerate(labels) if l == cluster_id]

        if len(cluster_points) < 2:
            continue

        # heurística: nearest neighbor
        ordered = [cluster_points[0]]
        remaining = cluster_points[1:]
        while remaining:
            last = ordered[-1]
            next_point = min(
                remaining,
                key=lambda p: ox.distance.great_circle_vec(last[0], last[1], p[0], p[1])
            )
            ordered.append(next_point)
            remaining.remove(next_point)

        cluster_routes = []
        for i in range(len(ordered) - 1):
            path = shortest_path(ordered[i], ordered[i + 1])
            cluster_routes.append({"route": {"geometry": [[(x, y) for x, y in path]]}})

            dist = ox.distance.great_circle_vec(
                ordered[i][0], ordered[i][1],
                ordered[i+1][0], ordered[i+1][1]
            ) / 1000.0  # km
            total_distance += dist
            total_eta += dist / 30 * 60  # média 30km/h

        routes.append({"cluster": cluster_id, "route": cluster_routes})

    return {
        "routes": routes,
        "total_distance_km": round(total_distance, 3),
        "total_eta_min": round(total_eta, 1),
        "clusters": clusters
    }
