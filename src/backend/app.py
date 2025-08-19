from flask import Flask, request, jsonify
from flask_cors import CORS
from optimizer import Point, optimize

app = Flask(__name__)
CORS(app)

@app.route("/optimize-route", methods=["POST"])
def optimize_route():
    try:
        data = request.get_json()
        points_data = data.get("points", [])
        k = data.get("k")

        points = [Point(p["id"], p["lat"], p["lon"], p.get("addr", "")) for p in points_data]

        result = optimize(points, k)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
