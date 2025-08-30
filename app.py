from flask import Flask, request, jsonify, send_from_directory
from api.geocode import get_coordinates
from api.optimizer import optimize_route_osrm, route_osrm
from api.clustering import cluster_points
from api.ml_model import DeliveryTimePredictor

app = Flask(__name__, static_folder="static", static_url_path="")

predictor = DeliveryTimePredictor()

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/geocode", methods=["POST"])
def geocode():
    data = request.json
    lat, lon = get_coordinates(data["address"])
    return jsonify({"lat": lat, "lon": lon})

@app.route("/optimize", methods=["POST"])
def optimize():
    data = request.json
    result = optimize_route_osrm(data["coords"])
    return jsonify(result)

@app.route("/route", methods=["POST"])
def route():
    data = request.json
    result = route_osrm(data["coords"])
    return jsonify(result)

@app.route("/cluster", methods=["POST"])
def cluster():
    data = request.json
    labels, centers = cluster_points(data["coords"], n_clusters=data.get("k", 2))
    return jsonify({"labels": labels.tolist(), "centers": centers.tolist()})

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    time = predictor.predict(data["distance"])
    return jsonify({"predicted_time": time})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
