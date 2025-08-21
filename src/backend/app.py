from flask import Flask, request, jsonify, send_from_directory
import os
from optimizer import optimize_routes
from geo import geocode_address

app = Flask(
    __name__,
    static_folder="../frontend/assets",
    template_folder="../frontend/assets"
)

# rota principal -> abre a interface
@app.route("/")
def index():
    return send_from_directory(app.template_folder, "index.html")

# rota para otimizar as rotas
@app.route("/optimize", methods=["POST"])
def optimize():
    data = request.get_json()
    addresses = data.get("addresses", [])
    clusters = int(data.get("clusters", 1))

    if not addresses:
        return jsonify({"error": "Nenhum endereço recebido"}), 400

    try:
        coords = [geocode_address(addr) for addr in addresses]
        route, distance_km, eta_min = optimize_routes(coords, clusters)
        return jsonify({
            "route": route,
            "distance_km": distance_km,
            "eta_min": eta_min
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# rota para servir os arquivos estáticos (js, css)
@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
