let map, layerGroup, drawMode = false;
let markers = [];
let polylines = [];

function initMap() {
  map = L.map('map').setView([-23.68, -46.85], 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19, attribution: '&copy; OpenStreetMap'
  }).addTo(map);
  layerGroup = L.layerGroup().addTo(map);

  map.on('click', (e) => {
    if (!drawMode) return;
    addDestination(e.latlng.lat, e.latlng.lng);
  });
}

function genId() {
  return Math.random().toString(36).slice(2, 7);
}

function addDestination(lat = '', lon = '') {
  const li = document.createElement('li');
  li.draggable = true;
  li.dataset.id = genId();

  li.innerHTML = `
    <span class="badge">#</span>
    <input class="lat" type="number" step="any" placeholder="lat" value="${lat}">
    <input class="lon" type="number" step="any" placeholder="lon" value="${lon}">
    <button class="focus">📍</button>
    <button class="remove">🗑️</button>
    <div class="coords"></div>
  `;

  // drag & drop
  li.addEventListener('dragstart', e => e.dataTransfer.setData('text/plain', li.dataset.id));
  li.addEventListener('dragover', e => e.preventDefault());
  li.addEventListener('drop', e => {
    e.preventDefault();
    const id = e.dataTransfer.getData('text/plain');
    const dragged = document.querySelector(`li[data-id="${id}"]`);
    li.parentNode.insertBefore(dragged, li);
    renumber();
  });

  li.querySelector('.remove').onclick = () => { li.remove(); renumber(); };
  li.querySelector('.focus').onclick = () => {
    const lat = parseFloat(li.querySelector('.lat').value);
    const lon = parseFloat(li.querySelector('.lon').value);
    if (isFinite(lat) && isFinite(lon)) map.setView([lat, lon], 15);
  };

  document.getElementById('dest-list').appendChild(li);
  renumber();
}

function renumber() {
  document.querySelectorAll('#dest-list li').forEach((li, idx) => {
    li.querySelector('.badge').textContent = String(idx + 1);
    const lat = li.querySelector('.lat').value;
    const lon = li.querySelector('.lon').value;
    li.querySelector('.coords').textContent = (lat && lon) ? `${lat}, ${lon}` : '';
  });
  renderMarkers();
}

function renderMarkers() {
  layerGroup.clearLayers();
  markers = [];
  document.querySelectorAll('#dest-list li').forEach((li, idx) => {
    const lat = parseFloat(li.querySelector('.lat').value);
    const lon = parseFloat(li.querySelector('.lon').value);
    if (isFinite(lat) && isFinite(lon)) {
      const m = L.marker([lat, lon], { draggable: true }).addTo(layerGroup);
      m.on('dragend', () => {
        const p = m.getLatLng();
        li.querySelector('.lat').value = p.lat.toFixed(6);
        li.querySelector('.lon').value = p.lng.toFixed(6);
        renumber();
      });
      m.bindTooltip(String(idx + 1), { permanent: true, direction: 'top' }).openTooltip();
      markers.push(m);
    }
  });
  polylines.forEach(p => layerGroup.removeLayer(p));
  polylines = [];
}

async function optimize() {
  const points = [];
  document.querySelectorAll('#dest-list li').forEach((li, idx) => {
    const lat = parseFloat(li.querySelector('.lat').value);
    const lon = parseFloat(li.querySelector('.lon').value);
    if (isFinite(lat) && isFinite(lon)) {
      points.push({ id: String(idx + 1), lat, lon });
    }
  });

  if (points.length < 2) {
    alert('Adicione pelo menos 2 destinos.');
    return;
  }

  const kStr = document.getElementById('k-input').value;
  const k = kStr ? Number(kStr) : undefined;

  const resp = await fetch('/optimize-route', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ points, k })
  });
  const data = await resp.json();
  if (data.error) { alert(data.error); return; }

  // desenhar clusters e rotas
  polylines.forEach(p => layerGroup.removeLayer(p));
  polylines = [];

  const palette = ['#3366cc','#dc3912','#ff9900','#109618','#990099','#0099c6','#dd4477'];
  let sumKm = 0, sumEta = 0;

  data.clusters.forEach((c, idx) => {
    const color = palette[idx % palette.length];
    const latlngs = c.points.map(p => [p.lat, p.lon]);
    const poly = L.polyline(latlngs, { weight: 5, opacity: 0.8, color }).addTo(layerGroup);
    polylines.push(poly);
    sumKm += c.distance_km;
    sumEta += c.eta_min;
  });

  document.getElementById('summary').innerHTML =
    `<b>Distância total:</b> ${data.total_km} km — ` +
    `<b>ETA total:</b> ${data.total_eta_min} min — ` +
    `<b>Clusters:</b> ${data.clusters.length}`;
}

function bindUI() {
  document.getElementById('add-dest').onclick = () => addDestination();
  document.getElementById('use-map').onclick = (e) => {
    drawMode = !drawMode;
    e.target.textContent = drawMode ? 'Parar clique no mapa' : 'Clique no mapa';
  };
  document.getElementById('optimize').onclick = optimize;
  document.getElementById('clear').onclick = () => {
    document.getElementById('dest-list').innerHTML = '';
    renumber();
  };
}

initMap();
bindUI();

// pontos de exemplo (Itapecerica e região)
[
  [-23.7168, -46.8492], [-23.7066, -46.8451],
  [-23.7015, -46.8335], [-23.7189, -46.8412]
].forEach(([lat, lon]) => addDestination(lat, lon));
