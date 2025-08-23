from flask import Flask, request, jsonify
from api.geocode import geocode_address
from api.optimizer import optimize_routes

app = Flask(__name__, static_folder="static", template_folder="static")


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/geocode", methods=["POST"])
def geocode():
    data = request.get_json(force=True) or {}
    address = (data.get("address") or "").strip()
    if not address:
        return jsonify({"error": "Endereço vazio"}), 400

    lat, lon, label = geocode_address(address)
    if lat is None:
        return jsonify({"error": "Endereço não encontrado"}), 404

    return jsonify({"lat": lat, "lon": lon, "label": label})


@app.route("/optimize", methods=["POST"])
def optimize():
    data = request.get_json(force=True) or {}
    points = data.get("points") or []
    if not isinstance(points, list) or len(points) < 2:
        return jsonify({"error": "São necessários ao menos 2 pontos"}), 400

    result = optimize_routes(points)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
