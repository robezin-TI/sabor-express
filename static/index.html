let map = L.map("map").setView([-23.5505, -46.6333], 12); // SP como default
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: "© OpenStreetMap contributors"
}).addTo(map);

let points = [];
let markers = [];
let routeLine = null;

// adicionar ponto por endereço
document.getElementById("add-btn").onclick = async () => {
  const addr = document.getElementById("address").value;
  if (!addr) return;
  const resp = await fetch("/geocode", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ address: addr })
  });
  const data = await resp.json();
  if (data.error) { alert(data.error); return; }
  addPoint(data.lat, data.lon, data.label);
};

// adicionar ponto clicando no mapa
document.getElementById("map-btn").onclick = () => {
  map.once("click", e => {
    addPoint(e.latlng.lat, e.latlng.lng, `(${e.latlng.lat.toFixed(4)}, ${e.latlng.lng.toFixed(4)})`);
  });
};

function addPoint(lat, lon, label) {
  const idx = points.length;
  points.push({ lat, lon, label });

  const marker = L.marker([lat, lon]).addTo(map).bindPopup(label);
  markers.push(marker);

  renderList();
}

function renderList() {
  const list = document.getElementById("points-list");
  list.innerHTML = "";
  points.forEach((p, i) => {
    const li = document.createElement("li");
    li.innerHTML = `<span>${String.fromCharCode(65 + i)} - ${p.label}</span>`;
    const delBtn = document.createElement("button");
    delBtn.innerText = "X";
    delBtn.className = "danger";
    delBtn.onclick = () => removePoint(i);
    li.appendChild(delBtn);
    list.appendChild(li);
  });
}

function removePoint(i) {
  points.splice(i, 1);
  map.removeLayer(markers[i]);
  markers.splice(i, 1);
  renderList();
  if (routeLine) { map.removeLayer(routeLine); routeLine = null; }
}

document.getElementById("clear-btn").onclick = () => {
  points = [];
  markers.forEach(m => map.removeLayer(m));
  markers = [];
  if (routeLine) { map.removeLayer(routeLine); routeLine = null; }
  renderList();
  document.getElementById("metrics").innerText = "";
};

document.getElementById("optimize-btn").onclick = async () => {
  if (points.length < 2) { alert("Adicione pelo menos 2 pontos"); return; }
  const resp = await fetch("/optimize", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ points })
  });
  const data = await resp.json();
  if (data.error) { alert(data.error); return; }

  // redesenha lista e rota
  points = data.ordered_points;
  markers.forEach(m => map.removeLayer(m));
  markers = [];
  points.forEach(p => {
    const marker = L.marker([p.lat, p.lon]).addTo(map).bindPopup(p.label);
    markers.push(marker);
  });

  if (routeLine) { map.removeLayer(routeLine); }
  routeLine = L.polyline(data.route, { color: "blue" }).addTo(map);
  map.fitBounds(routeLine.getBounds());

  document.getElementById("metrics").innerText =
    `Distância: ${data.distance_km} km | ETA: ${data.eta_min} min`;
};
