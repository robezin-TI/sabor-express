let map = L.map('map').setView([-23.55, -46.63], 11);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

let markers = [];
let points = [];

function addAddressBox(lat, lon, label="") {
  const container = document.getElementById("addresses");
  const div = document.createElement("div");
  div.className = "address-box";
  div.innerHTML = `
    <input type="text" value="${label}" readonly />
    <input type="text" value="${lat.toFixed(6)}, ${lon.toFixed(6)}" readonly />
  `;
  container.appendChild(div);
}

async function addAddress(address) {
  const res = await fetch("/geocode", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({address: address})
  });
  const data = await res.json();
  if(data.lat && data.lon){
    let marker = L.marker([data.lat, data.lon]).addTo(map).bindPopup(address);
    markers.push(marker);
    points.push([data.lat, data.lon]);
    addAddressBox(data.lat, data.lon, address);
  }
}

async function optimizeRoute() {
  const res = await fetch("/optimize", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({points: points})
  });
  const data = await res.json();
  if(data.route){
    let latlngs = data.route.map(p => [p[0], p[1]]);
    L.polyline(latlngs, {color: 'blue'}).addTo(map);
    document.getElementById("summary").innerText =
      `Distância total: ${data.distance_km} km — ETA: ${data.eta_min} min`;
  }
}

document.getElementById("addAddressBtn").addEventListener("click", () => {
  const addr = prompt("Digite o endereço:");
  if(addr) addAddress(addr);
});
document.getElementById("optimizeBtn").addEventListener("click", optimizeRoute);

