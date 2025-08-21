let map = L.map('map').setView([-23.55, -46.63], 12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

let clickMode = false;
let markers = [];   // [{marker, lat, lon, label}]
let polyline = null;

// helpers
function numberIcon(n) {
  return L.divIcon({
    className: 'num-icon',
    html: `<div style="
      background:#2b7cff;color:white;border-radius:14px;
      width:28px;height:28px;display:flex;align-items:center;justify-content:center;
      border:2px solid white; box-shadow: 0 0 4px rgba(0,0,0,.2);
      font-weight:600;">${n}</div>`,
    iconSize: [28, 28],
    iconAnchor: [14, 28]
  });
}

function refreshMarkers() {
  markers.forEach((m, i) => m.marker.setIcon(numberIcon(i+1)));
  renderList();
}

function renderList() {
  const wrap = document.getElementById('addresses');
  wrap.innerHTML = '';
  markers.forEach((m, i) => {
    const row = document.createElement('div');
    row.className = 'address';
    row.innerHTML = `
      <div class="idx">${i+1}</div>
      <input type="text" value="${m.label}" readonly />
      <button data-i="${i}" class="zoom">Ir</button>
      <button data-i="${i}" class="del">X</button>
    `;
    wrap.appendChild(row);
  });

  // eventos
  wrap.querySelectorAll('.zoom').forEach(btn => {
    btn.onclick = () => {
      const i = parseInt(btn.dataset.i);
      map.setView([markers[i].lat, markers[i].lon], 16);
      markers[i].marker.openPopup();
    };
  });
  wrap.querySelectorAll('.del').forEach(btn => {
    btn.onclick = () => {
      const i = parseInt(btn.dataset.i);
      map.removeLayer(markers[i].marker);
      markers.splice(i,1);
      if (polyline) { map.removeLayer(polyline); polyline = null; }
      refreshMarkers();
    };
  });
}

async function addAddress(address) {
  const res = await fetch('/geocode', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({address})
  });
  const data = await res.json();
  if (!res.ok) {
    alert(data.error || 'Endereço não encontrado');
    return;
  }
  const {lat, lon, label} = data;
  const m = L.marker([lat, lon], {icon: numberIcon(markers.length+1)}).addTo(map)
            .bindPopup(label);
  markers.push({marker: m, lat, lon, label});
  renderList();
}

map.on('click', (e) => {
  if (!clickMode) return;
  const lat = e.latlng.lat, lon = e.latlng.lng;
  const label = `Ponto ${markers.length+1}`;
  const m = L.marker([lat, lon], {icon: numberIcon(markers.length+1)}).addTo(map)
            .bindPopup(label);
  markers.push({marker: m, lat, lon, label});
  renderList();
});

document.getElementById('addAddressBtn').onclick = async () => {
  const addr = prompt('Digite o endereço:');
  if (addr) await addAddress(addr);
};

document.getElementById('clickModeBtn').onclick = () => {
  clickMode = !clickMode;
  document.getElementById('clickModeBtn').innerText = clickMode ? 'Clique no mapa (ON)' : 'Clique no mapa';
};

document.getElementById('clearBtn').onclick = () => {
  markers.forEach(m => map.removeLayer(m.marker));
  markers = [];
  if (polyline) { map.removeLayer(polyline); polyline = null; }
  renderList();
  document.getElementById('summary').innerText = 'Distância: 0 km — ETA: 0 min';
};

document.getElementById('optBtn').onclick = async () => {
  if (markers.length < 2) { alert('Adicione pelo menos dois pontos.'); return; }
  const points = markers.map(m => ({lat: m.lat, lon: m.lon, label: m.label}));
  const res = await fetch('/optimize', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({points})
  });
  const data = await res.json();
  if (!res.ok) { alert(data.error || 'Falha ao otimizar'); return; }

  // reordena marcadores conforme solução
  const idx = data.ordered_points.map(p => {
    return points.findIndex(q => q.lat === p.lat && q.lon === p.lon);
  });
  // ordenar nossa lista local
  markers = idx.map(i => markers[i]);
  refreshMarkers();

  // desenhar polilinha pelas ruas
  if (polyline) map.removeLayer(polyline);
  const latlngs = data.route.map(p => [p[0], p[1]]);
  polyline = L.polyline(latlngs, {weight: 5}).addTo(map);
  map.fitBounds(polyline.getBounds(), {padding: [30,30]});

  document.getElementById('summary').innerText =
    `Distância: ${data.distance_km} km — ETA: ${data.eta_min} min`;
};
