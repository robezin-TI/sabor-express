import networkx as nx
import osmnx as ox
from sklearn.cluster import KMeans
from statistics import mean

AVG_SPEED_KMH = 30.0  # motoboy
ox.config(log_console=False, use_cache=True)

def _meters_between(a, b):
    return ox.distance.great_circle_vec(a[0], a[1], b[0], b[1])

def build_graph(points):
    lat_mean = mean(p[0] for p in points)
    lon_mean = mean(p[1] for p in points)
    dist_m = max(2000, int(max(_meters_between((lat_mean, lon_mean), p) for p in points) * 1.3))
    return ox.graph_from_point((lat_mean, lon_mean), dist=dist_m, network_type="drive")

def route_between(G, a, b):
    orig = ox.distance.nearest_nodes(G, a[1], a[0])
    dest = ox.distance.nearest_nodes(G, b[1], b[0])
    path = nx.shortest_path(G, orig, dest, weight="length")

    dist_m = 0.0
    for u, v in zip(path[:-1], path[1:]):
        data = G.get_edge_data(u, v)
        if data:
            dist_m += min(d.get("length", 0.0) for d in data.values())

    poly = [[G.nodes[n]["y"], G.nodes[n]["x"]] for n in path]
    return poly, dist_m / 1000.0

def nearest_neighbor(points):
    if len(points) <= 2: return points
    ordered, rem = [points[0]], points[1:]
    while rem:
        last = ordered[-1]
        nxt = min(rem, key=lambda p: _meters_between(last, p))
        ordered.append(nxt); rem.remove(nxt)
    return ordered

def optimize_routes(addresses, clusters):
    coords = [tuple(a["coords"]) for a in addresses if "coords" in a]
    labels = [a.get("label", "") for a in addresses]

    if clusters > 1 and len(coords) >= clusters:
        km = KMeans(n_clusters=clusters, n_init=10, random_state=42)
        cluster_ids = km.fit_predict(coords)
    else:
        clusters, cluster_ids = 1, [0] * len(coords)

    G = build_graph(coords)
    total_km, total_min, routes_out = 0.0, 0.0, []

    for cid in sorted(set(cluster_ids)):
        cluster_pts = [coords[i] for i, lab in enumerate(cluster_ids) if lab == cid]
        ordered = nearest_neighbor(cluster_pts)
        label_map = {coords[i]: labels[i] for i in range(len(coords))}
        legs, cluster_km = [], 0.0

        for a, b in zip(ordered[:-1], ordered[1:]):
            poly, d_km = route_between(G, a, b)
            legs.append({
                "from": {"coords": list(a), "label": label_map.get(a)},
                "to": {"coords": list(b), "label": label_map.get(b)},
                "polyline": poly,
                "distance_km": round(d_km, 3),
                "eta_min": round((d_km / AVG_SPEED_KMH) * 60, 1),
            })
            cluster_km += d_km

        cluster_min = (cluster_km / AVG_SPEED_KMH) * 60
        total_km += cluster_km; total_min += cluster_min
        routes_out.append({
            "cluster": int(cid),
            "order": [list(p) for p in ordered],
            "legs": legs,
            "distance_km": round(cluster_km, 3),
            "eta_min": round(cluster_min, 1),
        })

    return {
        "clusters": clusters,
        "total_distance_km": round(total_km, 3),
        "total_eta_min": round(total_min, 1),
        "routes": routes_out
    }
