from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from src.backend.optimizer import optimize
from src.backend.geo import geocode_address
import os

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/geocode", methods=["POST"])
def geocode():
    data = request.get_json()
    address = data.get("address")
    coords = geocode_address(address)
    return jsonify({"coords": coords})

@app.route("/api/optimize", methods=["POST"])
def optimize_route():
    data = request.get_json()
    addresses = data.get("addresses", [])
    clusters = int(data.get("clusters", 1))
    result = optimize(addresses, clusters)
    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
