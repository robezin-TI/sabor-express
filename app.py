from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from optimizer import optimize_routes
from geo import geocode_address

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

@app.route("/")
def root():
    return send_from_directory("static", "index.html")

@app.route("/geocode", methods=["POST"])
def geocode():
    data = request.get_json(force=True)
    address = data.get("address", "")
    latlon = geocode_address(address)
    if not latlon:
        return jsonify({"error": "Endereço não encontrado"}), 404
    lat, lon = latlon
    return jsonify({"lat": lat, "lon": lon, "label": address})

@app.route("/optimize", methods=["POST"])
def optimize():
    data = request.get_json(force=True)
    points = data.get("points", [])
    if len(points) < 2:
        return jsonify({"ordered_points": points, "route": [], "distance_km": 0, "eta_min": 0})

    coords = [(p["lat"], p["lon"]) for p in points]
    route_coords, ordered_idx, dist_km, eta_min = optimize_routes(coords)

    ordered_points = [points[i] for i in ordered_idx]
    return jsonify({
        "ordered_points": ordered_points,
        "route": route_coords,          # lista de [lat, lon] seguindo as ruas
        "distance_km": dist_km,
        "eta_min": eta_min
    })

if __name__ == "__main__":
    # debug=True ajuda durante o desenvolvimento
    app.run(host="0.0.0.0", port=5000, debug=True)
