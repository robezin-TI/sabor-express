let map = L.map("map").setView([-23.55, -46.63], 10);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap"
}).addTo(map);

let markers = [];
let coords = [];

function addAddress() {
  const address = document.getElementById("address").value;
  fetch("/geocode", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({address})
  })
  .then(res => res.json())
  .then(data => {
    if (data.lat && data.lon) {
      coords.push([data.lat, data.lon]);
      let marker = L.marker([data.lat, data.lon]).addTo(map);
      markers.push(marker);
      updateList();
    }
  });
}

function updateList() {
  const list = document.getElementById("address-list");
  list.innerHTML = "";
  coords.forEach((c, i) => {
    let li = document.createElement("li");
    li.textContent = `(${c[0].toFixed(5)}, ${c[1].toFixed(5)})`;
    list.appendChild(li);
  });
}

function drawRoute() {
  fetch("/route", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({coords})
  })
  .then(res => res.json())
  .then(data => {
    showRoute(data);
  });
}

function optimizeRoute() {
  fetch("/optimize", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({coords})
  })
  .then(res => res.json())
  .then(data => {
    showRoute(data);
  });
}

let routeLayer;
function showRoute(data) {
  if (routeLayer) map.removeLayer(routeLayer);

  if (!data.routes && !data.trips) return;

  let route = data.routes ? data.routes[0] : data.trips[0];
  routeLayer = L.geoJSON(route.geometry).addTo(map);

  // Mostra instruções
  const steps = route.legs.flatMap(leg => leg.steps);
  const dirBox = document.getElementById("directions");
  dirBox.innerHTML = "";
  steps.forEach((s, i) => {
    const div = document.createElement("div");
    div.textContent = `${i+1}. ${s.maneuver.instruction || "Seguir"}`;
    dirBox.appendChild(div);
  });
}

function clearAll() {
  coords = [];
  markers.forEach(m => map.removeLayer(m));
  markers = [];
  if (routeLayer) map.removeLayer(routeLayer);
  document.getElementById("address-list").innerHTML = "";
  document.getElementById("directions").innerHTML = "";
}
