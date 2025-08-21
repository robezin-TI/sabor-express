import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from .optimizer import optimize_routes
from .geo import geocode_address

# caminho absoluto da pasta do frontend (robusto no Docker)
STATIC_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend", "assets")
)

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="/")
CORS(app)


@app.route("/")
def root():
    # abre a interface
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    # serve script.js, style.css, etc.
    return send_from_directory(STATIC_DIR, filename)


@app.route("/geocode", methods=["POST"])
def geocode():
    """Geocodifica um endereço (para botão '+ Adicionar endereço')."""
    data = request.get_json(force=True)
    address = data.get("address", "")
    latlon = geocode_address(address)
    if not latlon:
        return jsonify({"error": "Endereço não encontrado"}), 404
    lat, lon = latlon
    return jsonify({"lat": lat, "lon": lon, "label": address})


@app.route("/optimize", methods=["POST"])
def optimize():
    """
    Recebe pontos já com lat/lon (vindos do clique no mapa ou geocodificação)
    e retorna:
      - ordem ótima dos pontos
      - polilinha pelas ruas (lat,lon)
      - distância total (km) e ETA (min)
    """
    data = request.get_json(force=True)
    points = data.get("points", [])  # [{lat, lon, label}, ...]
    if len(points) < 2:
        return jsonify({"route": [p for p in points], "distance_km": 0, "eta_min": 0})

    # converter para lista de tuplas (lat,lon) mantendo rótulos
    coords = [(p["lat"], p["lon"]) for p in points]
    labels = [p.get("label") or f"Ponto {i+1}" for i, p in enumerate(points)]

    route_coords, ordered_idx, dist_km, eta_min = optimize_routes(coords)

    # reordena pontos conforme a solução
    ordered_points = [points[i] for i in ordered_idx]

    return jsonify({
        "ordered_points": ordered_points,
        "route": route_coords,          # polyline pelas RUAS
        "distance_km": dist_km,
        "eta_min": eta_min
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
