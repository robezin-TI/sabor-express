import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# garante que possamos importar geo/optimizer sem __init__.py
CURRENT_DIR = os.path.dirname(__file__)
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from geo import geocode_address          # noqa: E402
from optimizer import optimize_routes    # noqa: E402

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # /src
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(FRONTEND_DIR, path)

@app.route("/api/geocode", methods=["POST"])
def api_geocode():
    data = request.get_json(force=True)
    address = data.get("address")
    coords = geocode_address(address) if address else None
    return jsonify({"coords": coords})

@app.route("/api/optimize", methods=["POST"])
def api_optimize():
    payload = request.get_json(force=True) or {}
    addresses = payload.get("addresses", [])
    clusters = int(payload.get("clusters", 1) or 1)

    if len(addresses) < 2:
        return jsonify({"error": "Adicione pelo menos 2 endereços."}), 400

    try:
        result = optimize_routes(addresses, clusters)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
