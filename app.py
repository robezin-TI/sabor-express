import os
from flask import Flask, request, jsonify, send_from_directory
from api.geocode import geocode_address
from api.optimizer import optimize_routes
from api.clustering import kmeans_clusters
from api.ml_model import MODEL

app = Flask(__name__, static_folder="static", static_url_path="")

# ---------- Static ----------
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

# ---------- API ----------
@app.route("/api/geocode", methods=["POST"])
def api_geocode():
    data = request.get_json(silent=True) or {}
    address = data.get("address", "")
    res = geocode_address(address)
    return jsonify(res), (200 if "error" not in res else 400)

@app.route("/api/astar", methods=["POST"])
def api_astar():
    data = request.get_json(silent=True) or {}
    points = data.get("points", [])
    if len(points) < 2:
        return jsonify({"error": "Envie ao menos 2 pontos"}), 400
    nodes, dist_km, time_min = optimize_routes(points)
    return jsonify({"nodes": nodes, "distance_km": dist_km, "time_min": time_min})

@app.route("/api/cluster", methods=["POST"])
def api_cluster():
    data = request.get_json(silent=True) or {}
    points = data.get("points", [])
    k = int(data.get("k", 2))
    res = kmeans_clusters(points, k=k)
    return jsonify(res)

@app.route("/api/ml/predict", methods=["POST"])
def api_predict():
    data = request.get_json(silent=True) or {}
    distance_km = float(data.get("distance_km", 0))
    stops = int(data.get("stops", 0))
    pred = MODEL.predict(distance_km, stops)
    return jsonify({"prediction_min": round(pred, 2)})

# ---------- Run ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)
