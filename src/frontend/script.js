// --------- MAPA ---------
const map = L.map('map').setView([-23.716, -46.849], 12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors'
}).addTo(map);

let addresses = [];   // {label, coords:[lat,lon], input:HTMLInputElement}
let markers = [];
let polylines = [];

const elList = document.getElementById('addressList');
const elSummary = document.getElementById('summary');

document.getElementById('btnAdd').onclick = () => addAddressRow();
document.getElementById('btnMapClick').onclick = enableMapClick;
document.getElementById('btnOptimize').onclick = optimizeRoute;
document.getElementById('btnClear').onclick = clearAll;

function divIconNumber(n){
  return L.divIcon({
    className: 'custom-div-icon',
    html: `<div class="marker-number">${n}</div>`,
    iconSize: [30, 42],
    iconAnchor: [15, 42]
  });
}

function refreshMarkers(){
  markers.forEach(m => map.removeLayer(m));
  markers = [];
  addresses.forEach((a, i) => {
    if(a.coords){
      const m = L.marker([a.coords[0], a.coords[1]], {icon: divIconNumber(i+1)}).addTo(map);
      markers.push(m);
    }
  });
}

function drawPolylines(routes){
  polylines.forEach(p => map.removeLayer(p));
  polylines = [];
  routes.forEach(r => {
    r.legs.forEach(leg => {
      const latlngs = leg.polyline.map(p => [p[0], p[1]]);
      polylines.push(L.polyline(latlngs).addTo(map));
    });
  });
}

function addAddressRow(prefill=""){
  const idx = addresses.length + 1;
  const row = document.createElement('div');
  row.className = 'row';
  row.innerHTML = `
    <span class="badge">${idx}</span>
    <input type="text" placeholder="Endereço ou 'lat, lon'" value="${prefill}">
    <button class="pill mini">🔍</button>
    <button class="pill mini">🗑️</button>
  `;
  elList.appendChild(row);

  const input = row.querySelector('input');
  const btnGo = row.querySelectorAll('button')[0];
  const btnDel = row.querySelectorAll('button')[1];

  addresses.push({label: "", coords: null, input});

  btnGo.onclick = async () => {
    const raw = input.value.trim();
    if(!raw) return;

    // aceita "lat, lon" direto
    const latlon = raw.match(/^\s*(-?\d+(\.\d+)?)\s*,\s*(-?\d+(\.\d+)?)\s*$/);
    if(latlon){
      const lat = parseFloat(latlon[1]), lon = parseFloat(latlon[3]);
      setAddressCoords(input, [lat, lon], raw);
      return;
    }

    const r = await fetch('/api/geocode', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({address: raw})
    });
    const j = await r.json();
    if(j.coords){
      setAddressCoords(input, j.coords, raw);
    }else{
      alert("Endereço não encontrado.");
    }
  };

  btnDel.onclick = () => {
    addresses = addresses.filter(a => a.input !== input);
    elList.removeChild(row);
    reindexListBadges();
    refreshMarkers();
    drawPolylines([]); // limpa rotas se necessário
  };
}

function setAddressCoords(inputEl, coords, label){
  const i = addresses.findIndex(a => a.input === inputEl);
  if(i >= 0){
    addresses[i].coords = coords;
    addresses[i].label = label;
  }
  refreshMarkers();
  map.setView([coords[0], coords[1]], 14);
}

function reindexListBadges(){
  [...document.querySelectorAll('#addressList .row .badge')]
    .forEach((b, i) => b.textContent = (i+1));
}

function enableMapClick(){
  map.once('click', e => {
    const lat = e.latlng.lat, lon = e.latlng.lng;
    addAddressRow(`${lat.toFixed(6)}, ${lon.toFixed(6)}`);
    const input = addresses[addresses.length-1].input;
    setAddressCoords(input, [lat,lon], input.value);
  });
}

function clearAll(){
  addresses = [];
  elList.innerHTML = "";
  elSummary.textContent = "";
  refreshMarkers();
  drawPolylines([]);
}

async function optimizeRoute(){
  const payload = addresses.filter(a => a.coords).map(a => ({label:a.label, coords:a.coords}));
  if(payload.length < 2){
    alert("Adicione pelo menos 2 endereços geocodificados (🔍).");
    return;
  }
  const clusters = parseInt(document.getElementById('clusters').value || "1", 10);

  const r = await fetch('/api/optimize', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({addresses: payload, clusters})
  });
  const data = await r.json();
  if(data.error){ alert(data.error); return; }

  drawPolylines(data.routes);

  // Reconstrói a lista na sequência otimizada (concatenando clusters)
  const ordered = [];
  data.routes.forEach(r => r.order.forEach(p => ordered.push(p)));

  // Recria UI com os labels existentes, quando possível (melhor esforço)
  const key = (p)=>`${p[0].toFixed(6)},${p[1].toFixed(6)}`;
  const labelMap = {};
  payload.forEach(a => { labelMap[key(a.coords)] = a.label; });

  elList.innerHTML = "";
  addresses = [];
  ordered.forEach(p => {
    addAddressRow(labelMap[key(p)] || "");
    const last = addresses[addresses.length-1];
    last.coords = p;
    last.label  = labelMap[key(p)] || last.label || "";
  });
  refreshMarkers();
  reindexListBadges();

  elSummary.textContent =
    `Distância total: ${data.total_distance_km} km — ETA total: ${data.total_eta_min} min — Clusters: ${data.clusters}`;
}
