let map = L.map('map').setView([-23.55, -46.63], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
}).addTo(map);

let points = [];
let markers = [];
let polyline = null;

const list = document.getElementById("points-list");

function updateList() {
    list.innerHTML = "";
    points.forEach((p, i) => {
        const item = document.createElement("li");
        item.textContent = p.label;

        const btnRemove = document.createElement("button");
        btnRemove.textContent = "❌";
        btnRemove.onclick = () => removePoint(i);

        const btnUp = document.createElement("button");
        btnUp.textContent = "⬆";
        btnUp.onclick = () => movePoint(i, -1);

        const btnDown = document.createElement("button");
        btnDown.textContent = "⬇";
        btnDown.onclick = () => movePoint(i, 1);

        item.append(" ", btnRemove, btnUp, btnDown);
        list.appendChild(item);
    });
}

function addPoint(lat, lon, label) {
    const marker = L.marker([lat, lon]).addTo(map);
    markers.push(marker);
    points.push({ lat, lon, label });
    updateList();
}

function removePoint(index) {
    map.removeLayer(markers[index]);
    markers.splice(index, 1);
    points.splice(index, 1);
    updateList();
    if (polyline) {
        map.removeLayer(polyline);
        polyline = null;
    }
}

function movePoint(index, direction) {
    const newIndex = index + direction;
    if (newIndex < 0 || newIndex >= points.length) return;

    const [point] = points.splice(index, 1);
    const [marker] = markers.splice(index, 1);
    points.splice(newIndex, 0, point);
    markers.splice(newIndex, 0, marker);

    updateList();
}

document.getElementById("add-btn").onclick = async () => {
    const address = document.getElementById("address").value;
    if (!address) return;
    const res = await fetch("/geocode", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ address })
    });
    const data = await res.json();
    if (data.lat) {
        addPoint(data.lat, data.lon, data.label);
        map.setView([data.lat, data.lon], 14);
    }
};

document.getElementById("map-btn").onclick = () => {
    map.once("click", (e) => {
        addPoint(e.latlng.lat, e.latlng.lng, `Ponto ${points.length + 1}`);
    });
};

document.getElementById("clear-btn").onclick = () => {
    points = [];
    markers.forEach(m => map.removeLayer(m));
    markers = [];
    if (polyline) map.removeLayer(polyline);
    polyline = null;
    updateList();
};

document.getElementById("optimize-btn").onclick = async () => {
    if (points.length < 2) return;

    const res = await fetch("/optimize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ points })
    });
    const data = await res.json();

    if (polyline) map.removeLayer(polyline);

    polyline = L.polyline(data.route, { color: "blue" }).addTo(map);
    map.fitBounds(polyline.getBounds());

    points = data.ordered_points;
    updateList();
};
