from flask import Flask, request, jsonify, send_from_directory
from api.geocode import get_coordinates
from api.optimizer import shortest_path
from api.clustering import cluster_deliveries
from api.ml_model import train_model, predict_sales

app = Flask(__name__, static_folder="static")


@app.route('/')
def index():
    return send_from_directory("static", "index.html")

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory("static", path)


# -------------------- API ROUTES --------------------

@app.route('/api/geocode', methods=['POST'])
def api_geocode():
    data = request.json
    address = data.get("address")
    coords = get_coordinates(address)
    return jsonify(coords)


@app.route('/api/route', methods=['POST'])
def api_route():
    data = request.json
    start = tuple(data["start"])
    end = tuple(data["end"])
    graph = data["graph"]
    path = shortest_path(graph, start, end)
    return jsonify({"path": path})


@app.route('/api/cluster', methods=['POST'])
def api_cluster():
    data = request.json
    points = data["points"]
    k = data.get("k", 2)
    clusters = cluster_deliveries(points, k)
    return jsonify(clusters)


@app.route('/api/train', methods=['POST'])
def api_train():
    data = request.json
    model_info = train_model(data["features"], data["targets"])
    return jsonify(model_info)


@app.route('/api/predict', methods=['POST'])
def api_predict():
    data = request.json
    prediction = predict_sales(data["features"])
    return jsonify({"prediction": prediction})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
