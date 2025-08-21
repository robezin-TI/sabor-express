from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from .optimizer import optimize_routes
from .geo import geocode_address

app = Flask(__name__, static_folder="../frontend/assets", static_url_path="/")
CORS(app)


@app.route("/")
def index():
    return send_from_directory("../frontend/assets", "index.html")


@app.route("/optimize", methods=["POST"])
def optimize():
    data = request.json
    addresses = data.get("addresses", [])
    clusters = data.get("clusters", 1)

    # geocodificar endereços
    coords = [geocode_address(addr) for addr in addresses]

    # otimizar rotas
    route, distance, eta = optimize_routes(coords, clusters)

    return jsonify({
        "route": route,
        "distance_km": distance,
        "eta_min": eta
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
