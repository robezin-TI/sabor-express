let map = L.map("map").setView([-23.5505, -46.6333], 12); // São Paulo default

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "&copy; OpenStreetMap contributors"
}).addTo(map);

let markers = [];
let points = [];

function renderList() {
  const ul = document.getElementById("points-list");
  ul.innerHTML = "";
  points.forEach((p, idx) => {
    let li = document.createElement("li");
    li.textContent = `${idx + 1}. ${p.label}`;
    let btn = document.createElement("button");
    btn.textContent = "X";
    btn.onclick = () => {
      map.removeLayer(markers[idx]);
      markers.splice(idx, 1);
      points.splice(idx, 1);
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
    method: "POST",
    headers: {"Content-Type": "application/json"},
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
  map.once("click", (e) => {
    let marker = L.marker([e.latlng.lat, e.latlng.lng]).addTo(map);
    markers.push(marker);
    points.push({lat: e.latlng.lat, lon: e.latlng.lng, label: "Mapa"});
    renderList();
  });
};

document.getElementById("clear-btn").onclick = () => {
  markers.forEach(m => map.removeLayer(m));
  markers = [];
  points = [];
  renderList();
  document.getElementById("metrics").innerHTML = "";
};

document.getElementById("optimize-btn").onclick = async () => {
  if (points.length < 2) return alert("Adicione pelo menos 2 pontos");

  let res = await fetch("/optimize", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({points})
  });

  let data = await res.json();
  if (data.error) {
    alert(data.error);
    return;
  }

  document.getElementById("metrics").innerHTML =
    `Distância: ${data.distance_km} km<br>Tempo: ${data.time_min} min`;
};
