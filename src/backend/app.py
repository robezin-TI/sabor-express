import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from optimizer import Point, optimize

# cria o app apontando para a pasta do frontend
app = Flask(__name__, static_folder="../frontend", static_url_path="/")
CORS(app)

# -----------------------------
# rota principal -> index.html
# -----------------------------
@app.route("/")
def index():
    return app.send_static_file("index.html")

# -----------------------------
# rota da API -> otimização
# -----------------------------
@app.route("/optimize-route", methods=["POST"])
def optimize_route():
    try:
        data = request.get_json(force=True)
        points_data = data.get("points", [])
        k = data.get("k")

        points = [Point(p["id"], p["lat"], p["lon"], p.get("addr", "")) for p in points_data]
        result = optimize(points, k)

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------
# servir arquivos estáticos (JS, CSS, etc.)
# -----------------------------
@app.route("/<path:path>")
def static_files(path):
    file_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
    return send_from_directory(file_dir, path)

# -----------------------------
# entrypoint
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
