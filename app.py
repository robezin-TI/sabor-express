from flask import Flask, request, jsonify, send_from_directory
from api.geocode import geocode_address
from api.optimizer import optimize_routes
import os

app = Flask(__name__, static_folder="static")

# Página inicial (carrega index.html do static)
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

# Endpoint para geocodificação de endereços
@app.route("/geocode", methods=["POST"])
def geocode():
    data = request.get_json()
    address = data.get("address")

    if not address:
        return jsonify({"error": "Endereço não fornecido"}), 400

    coords = geocode_address(address)
    if not coords:
        return jsonify({"error": "Endereço não encontrado"}), 404

    return jsonify({"lat": coords[0], "lon": coords[1]})

# Endpoint para otimizar rotas
@app.route("/optimize", methods=["POST"])
def optimize():
    data = request.get_json()
    points = data.get("points")

    if not points or len(points) < 2:
        return jsonify({"error": "Forneça pelo menos 2 pontos"}), 400

    try:
        route = optimize_routes(points)
        return jsonify({"route": route})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
