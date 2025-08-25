from flask import Flask, request, jsonify, send_from_directory
from api.geocode import geocode_address
from api.optimizer import optimize_routes
import os

app = Flask(__name__, static_folder="static", static_url_path="")

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/geocode", methods=["POST"])
def geocode():
    data = request.json
    address = data.get("address")
    coords = geocode_address(address)
    return jsonify(coords)

@app.route("/optimize", methods=["POST"])
def optimize():
    data = request.json
    points = data.get("points", [])
    if len(points) < 2:
        return jsonify({"error": "Mínimo de 2 pontos necessários"}), 400
    route, dist, time = optimize_routes(points)
    return jsonify({
        "route": route,
        "distance_km": dist,
        "time_min": time
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
