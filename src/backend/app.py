from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from .optimizer import optimize_routes
from .geo import geocode_address

app = Flask(__name__, static_folder="../frontend/assets")
CORS(app)

# rota para frontend
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

# rota para geocodificação de endereço -> coordenadas
@app.route("/geocode", methods=["POST"])
def geocode():
    data = request.get_json()
    address = data.get("address")
    coords = geocode_address(address)
    if coords:
        return jsonify({"lat": coords[0], "lon": coords[1]})
    return jsonify({"error": "Endereço não encontrado"}), 404

# rota para otimizar rotas
@app.route("/optimize", methods=["POST"])
def optimize():
    data = request.get_json()
    points = data.get("points", [])
    optimized, dist, time = optimize_routes(points)
    return jsonify({"route": optimized, "distance_km": dist, "eta_min": time})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
