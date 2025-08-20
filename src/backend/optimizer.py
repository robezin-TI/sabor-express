import osmnx as ox
import networkx as nx
from sklearn.cluster import KMeans
import itertools
import math

# Velocidade média do entregador (km/h)
AVG_SPEED = 30  

def haversine(coord1, coord2):
    """Distância geodésica aproximada em km."""
    R = 6371
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def optimize(addresses, clusters=1):
    if not addresses:
        return {"error": "Nenhum endereço fornecido"}

    # Cria grafo da região (dirigível)
    G = ox.graph_from_place("Itapecerica da Serra, Brazil", network_type="drive")

    # Coordenadas
    coords = [tuple(addr["coords"]) for addr in addresses]

    # Clusterização
    if clusters > 1:
        kmeans = KMeans(n_clusters=clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(coords)
    else:
        labels = [0] * len(coords)

    optimized_routes = []
    total_distance = 0
    total_time = 0

    for cluster_id in set(labels):
        cluster_points = [coords[i] for i in range(len(coords)) if labels[i] == cluster_id]

        # TSP: testa todas permutações
        best_route = None
        best_distance = float("inf")

        for perm in itertools.permutations(cluster_points):
            dist = 0
            path_segments = []

            for i in range(len(perm) - 1):
                orig_node = ox.distance.nearest_nodes(G, perm[i][1], perm[i][0])
                dest_node = ox.distance.nearest_nodes(G, perm[i+1][1], perm[i+1][0])

                # Rota com A*
                route = nx.astar_path(G, orig_node, dest_node, weight="length")
                length = sum(ox.utils_graph.get_route_edge_attributes(G, route, 'length'))
                dist += length / 1000  # metros -> km
                path_segments.append(ox.utils_graph.route_to_geometry(G, route))

            if dist < best_distance:
                best_distance = dist
                best_route = {"order": perm, "geometry": [list(seg.coords) for seg in path_segments]}

        eta = (best_distance / AVG_SPEED) * 60  # min
        total_distance += best_distance
        total_time += eta

        optimized_routes.append({
            "cluster": cluster_id,
            "distance_km": round(best_distance, 2),
            "eta_min": round(eta, 1),
            "route": best_route
        })

    return {
        "clusters": len(set(labels)),
        "total_distance_km": round(total_distance, 2),
        "total_eta_min": round(total_time, 1),
        "routes": optimized_routes
    }
