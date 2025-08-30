from flask import Flask, request, jsonify, send_from_directory
from api.geocode import get_coordinates
from api.clustering import cluster_points
from api.optimizer import a_star
from api.ml_model import predict

app = Flask(__name__, static_folder="static")

@app.route("/")
def serve_index():
    return send_from_directory("static", "index.html")

@app.route("/api/geocode", methods=["POST"])
def geocode():
    data = request.json
    coords = get_coordinates(data["address"])
    return jsonify(coords)

@app.route("/api/cluster", methods=["POST"])
def cluster():
    data = request.json
    clustered, centers = cluster_points(data["points"], n_clusters=data.get("n_clusters", 3))
    return jsonify({"points": clustered, "centers": centers})

@app.route("/api/optimize", methods=["POST"])
def optimize():
    data = request.json
    path = a_star(data["points"])
    return jsonify({"path": path})

@app.route("/api/predict", methods=["POST"])
def ml_predict():
    data = request.json
    value = data.get("value", 1)
    result = predict(value)
    return jsonify({"prediction": result})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
