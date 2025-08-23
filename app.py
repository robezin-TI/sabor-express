from flask import Flask, request, jsonify, render_template
from geo import geocode_address
from optimizer import optimize_routes

app = Flask(__name__, static_folder="static", template_folder="static")


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/geocode", methods=["POST"])
def geocode():
    data = request.get_json()
    address = data.get("address")
    lat, lon, label = geocode_address(address)
    return jsonify({"lat": lat, "lon": lon, "label": label})


@app.route("/optimize", methods=["POST"])
def optimize():
    data = request.get_json()
    points = data.get("points", [])
    route, ordered_points = optimize_routes(points)
    return jsonify({"route": route, "ordered_points": ordered_points})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
