let map = L.map("map").setView([-23.55, -46.63], 12);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap"
}).addTo(map);

let markers = [];
let points = [];
let routeLayer = null;

function renderList() {
  const ul = document.getElementById("points-list");
  ul.innerHTML = "";
  points.forEach((p, i) => {
    let li = document.createElement("li");
    li.textContent = `${String.fromCharCode(65+i)} - ${p.label}`;
    let btn = document.createElement("button");
    btn.textContent = "X";
    btn.onclick = () => {
      map.removeLayer(markers[i]);
      markers.splice(i, 1);
      points.splice(i, 1);
      renderList();
    };
    li.appendChild(btn);
    ul.appendChild(li);
  });
}

document.getElementById("add-btn").onclick = async () => {
  const addr = document.getElementById("address").value;
  if (!addr) return;
  let res = await fetch("/geocode", {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({address: addr})
  });
  let data = await res.json();
  if (data.lat && data.lon) {
    let marker = L.marker([data.lat, data.lon]).addTo(map);
    markers.push(marker);
    points.push({lat: data.lat, lon: data.lon, label: addr});
    renderList();
  }
};

document.getElementById("map-btn").onclick = () => {
  map.once("click", e => {
    let marker = L.marker([e.latlng.lat, e.latlng.lng]).addTo(map);
    markers.push(marker);
    points.push({lat: e.latlng.lat, lon: e.latlng.lng, label: "Mapa"});
    renderList();
  });
};

document.getElementById("clear-btn").onclick = () => {
  markers.forEach(m => map.removeLayer(m));
  if (routeLayer) map.removeLayer(routeLayer);
  markers = [];
  points = [];
  document.getElementById("metrics").innerHTML = "";
  renderList();
};

document.getElementById("optimize-btn").onclick = async () => {
  if (points.length < 2) return alert("Adicione pelo menos 2 pontos");

  let res = await fetch("/optimize", {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({points})
  });

  let data = await res.json();
  if (data.error) return alert(data.error);

  if (routeLayer) map.removeLayer(routeLayer);
  routeLayer = L.polyline([], {color:"blue"}).addTo(map);

  document.getElementById("metrics").innerHTML =
    `Distância: ${data.distance_km} km<br>Tempo: ${data.time_min} min`;
};
