import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from typing import List
from src.backend.optimizer import Point, optimize  # import absoluto

app = Flask(__name__, static_folder="../frontend", static_url_path="/")
CORS(app)

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/optimize-route", methods=["POST"])
def optimize_route():
    """
    JSON esperado:
    {
      "points": [{"id":"A","lat":-23.6,"lon":-46.9}, ...],
      "k": 2
    }
    """
    data = request.get_json(force=True)
    raw_points: List[dict] = data.get("points", [])
    k = data.get("k", None)

    if len(raw_points) < 2:
        return jsonify({"error": "Forneça pelo menos 2 pontos."}), 400

    points = [Point(id=str(p.get("id", i)),
                    lat=float(p["lat"]),
                    lon=float(p["lon"]))
              for i, p in enumerate(raw_points)]

    result = optimize(points, k_clusters=k)
    return jsonify(result)

@app.route("/<path:path>")
def static_proxy(path):
    file_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
    return send_from_directory(file_dir, path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
