// ====== MAPA ======
const map = L.map("map").setView([-23.55052, -46.63331], 13);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19
}).addTo(map);

// ====== ESTADO ======
let points = [];   // [{lat, lon, label}]
let markers = [];  // L.marker[]
let polyline = null;

const listEl = document.getElementById("points-list");
const metricsEl = document.getElementById("metrics");

// ====== UI LISTA ======
function renderList() {
  listEl.innerHTML = "";
  points.forEach((p, idx) => {
    const li = document.createElement("li");

    const badge = document.createElement("span");
    badge.className = "badge";
    badge.textContent = (idx + 1).toString();

    const label = document.createElement("span");
    label.className = "label";
    label.textContent = p.label;

    const actions = document.createElement("span");
    actions.className = "actions";

    const up = document.createElement("button");
    up.title = "Mover para cima";
    up.textContent = "⬆";
    up.onclick = () => movePoint(idx, -1);

    const down = document.createElement("button");
    down.title = "Mover para baixo";
    down.textContent = "⬇";
    down.onclick = () => movePoint(idx, 1);

    const del = document.createElement("button");
    del.title = "Remover ponto";
    del.textContent = "❌";
    del.onclick = () => removePoint(idx);

    actions.append(up, down, del);
    li.append(badge, label, actions);
    listEl.appendChild(li);
  });
}

// ====== ESTADO: ADICIONAR/REMOVER/MOVER ======
function addPoint(lat, lon, label) {
  const m = L.marker([lat, lon]).addTo(map);
  markers.push(m);
  points.push({ lat, lon, label });
  renderList();
}

function removePoint(index) {
  if (markers[index]) {
    map.removeLayer(markers[index]);
  }
  markers.splice(index, 1);
  points.splice(index, 1);
  renderList();
  clearRoute();
}

function movePoint(index, direction) {
  const newIndex = index + direction;
  if (newIndex < 0 || newIndex >= points.length) return;

  // Pontos
  const [p] = points.splice(index, 1);
  points.splice(newIndex, 0, p);

  // Marcadores
  const [m] = markers.splice(index, 1);
  markers.splice(newIndex, 0, m);

  renderList();
  clearRoute();
}

// ====== MÉTRICAS ======
function updateMetrics(routeCoords) {
  if (!routeCoords || routeCoords.length < 2) {
    metricsEl.textContent = "";
    return;
  }
  let distKm = 0;
  for (let i = 1; i < routeCoords.length; i++) {
    // distância aproximada: haversine simples (em km)
    const [lat1, lon1] = routeCoords[i - 1];
    const [lat2, lon2] = routeCoords[i];
    const R = 6371;
    const toRad = (d) => (d * Math.PI) / 180;
    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);
    const a =
      Math.sin(dLat / 2) ** 2 +
      Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    distKm += R * c;
  }
  const velocidade_kmh = 25; // média moto
  const eta_min = Math.round((distKm / velocidade_kmh) * 60);

  metricsEl.textContent = `Distância aprox.: ${distKm.toFixed(
    2
  )} km — ETA: ${eta_min} min`;
}

// ====== ROTA ======
function clearRoute() {
  if (polyline) {
    map.removeLayer(polyline);
    polyline = null;
  }
  updateMetrics(null);
}

async function optimizeRoute() {
  if (points.length < 2) return;

  const res = await fetch("/optimize", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ points })
  });

  const data = await res.json();
  if (!data.route || !Array.isArray(data.route) || data.route.length === 0) {
    alert("Não foi possível calcular a rota.");
    return;
  }

  clearRoute();
  polyline = L.polyline(data.route, { color: "dodgerblue", weight: 5 }).addTo(
    map
  );
  map.fitBounds(polyline.getBounds());

  // Mantemos a ordem enviada (o A* calcula o traçado entre elas)
  // Caso deseje TSP no futuro, é aqui que atualizaria 'points' pela ordem ótima.
  // points = data.ordered_points;
  renderList();
  updateMetrics(data.route);
}

// ====== HANDLERS ======
document.getElementById("add-btn").onclick = async () => {
  const address = document.getElementById("address").value.trim();
  if (!address) return;

  const res = await fetch("/geocode", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ address })
  });

  const data = await res.json();
  if (data.error || !data.lat) {
    alert("Endereço não encontrado.");
    return;
  }

  addPoint(data.lat, data.lon, data.label || address);
  map.setView([data.lat, data.lon], 15);
};

document.getElementById("map-btn").onclick = () => {
  map.once("click", (e) => {
    addPoint(e.latlng.lat, e.latlng.lng, `Ponto ${points.length + 1}`);
  });
};

document.getElementById("clear-btn").onclick = () => {
  points = [];
  markers.forEach((m) => map.removeLayer(m));
  markers = [];
  clearRoute();
  renderList();
};

document.getElementById("optimize-btn").onclick = optimizeRoute;

// Render inicial
renderList();
