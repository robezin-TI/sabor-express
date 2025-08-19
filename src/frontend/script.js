let map, layerGroup, drawMode = false;
let markers = [];
let polylines = [];

function initMap() {
  map = L.map('map').setView([-23.68, -46.85], 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19, attribution: '&copy; OpenStreetMap'
  }).addTo(map);
  layerGroup = L.layerGroup().addTo(map);

  map.on('click', async (e) => {
    if (!drawMode) return;
    const { lat, lng } = e.latlng;
    const addr = await reverseGeocode(lat, lng);
    const li = addDestination(addr || '');
    li.dataset.lat = lat;
    li.dataset.lon = lng;
    li.querySelector('.coords').textContent = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
    renderMarkers();
  });
}

function genId() { return Math.random().toString(36).slice(2, 7); }

function addDestination(address = '') {
  const li = document.createElement('li');
  li.draggable = true;
  li.dataset.id = genId();
  li.innerHTML = `
    <span class="badge">#</span>
    <input class="addr" type="text" placeholder="Digite um endereço" value="${address}">
    <button class="geocode" title="Buscar coordenadas">🔍</button>
    <button class="remove" title="Remover">🗑️</button>
    <div class="coords"></div>
  `;
  li.addEventListener('dragstart', e => e.dataTransfer.setData('text/plain', li.dataset.id));
  li.addEventListener('dragover', e => e.preventDefault());
  li.addEventListener('drop', e => { e.preventDefault();
    const id = e.dataTransfer.getData('text/plain');
    const dragged = document.querySelector(`li[data-id="${id}"]`);
    li.parentNode.insertBefore(dragged, li); renumber();
  });
  li.querySelector('.remove').onclick = () => { li.remove(); renumber(); };
  li.querySelector('.geocode').onclick = async () => { await ensureCoordinates(li); };
  li.querySelector('.addr').addEventListener('keydown', async (e) => {
    if (e.key === 'Enter') { e.preventDefault(); await ensureCoordinates(li); }
  });
  document.getElementById('dest-list').appendChild(li);
  renumber();
  return li;
}

function renumber() {
  document.querySelectorAll('#dest-list li').forEach((li, idx) => {
    li.querySelector('.badge').textContent = String(idx + 1);
  });
  renderMarkers();
}

function clearMapLayers() {
  layerGroup.clearLayers();
  polylines = [];
  markers = [];
}

function renderMarkers() {
  clearMapLayers();
  document.querySelectorAll('#dest-list li').forEach((li, idx) => {
    const lat = parseFloat(li.dataset.lat);
    const lon = parseFloat(li.dataset.lon);
    if (isFinite(lat) && isFinite(lon)) {
      const m = L.marker([lat, lon], { draggable: true }).addTo(layerGroup);
      m.on('dragend', async () => {
        const p = m.getLatLng();
        li.dataset.lat = p.lat;
        li.dataset.lon = p.lng;
        li.querySelector('.coords').textContent = `${p.lat.toFixed(6)}, ${p.lng.toFixed(6)}`;
        const addr = await reverseGeocode(p.lat, p.lng);
        if (addr) li.querySelector('.addr').value = addr;
        renumber();
      });
      m.bindTooltip(String(idx + 1), { permanent: true, direction: 'top' }).openTooltip();
      markers.push(m);
    }
  });
}

async function geocode(address) {
  if (!address) return null;
  const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(address)}&format=json&limit=1`;
  const res = await fetch(url, { headers: { 'Accept-Language': 'pt-BR' }});
  if (!res.ok) return null;
  const data = await res.json();
  if (!Array.isArray(data) || data.length === 0) return null;
  return { lat: parseFloat(data[0].lat), lon: parseFloat(data[0].lon), display: data[0].display_name };
}

async function reverseGeocode(lat, lon) {
  const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`;
  const res = await fetch(url, { headers: { 'Accept-Language': 'pt-BR' }});
  if (!res.ok) return '';
  const data = await res.json();
  return data.display_name || '';
}

async function ensureCoordinates(li) {
  const has = isFinite(parseFloat(li.dataset.lat)) && isFinite(parseFloat(li.dataset.lon));
  if (has) return true;
  const addr = li.querySelector('.addr').value.trim();
  if (!addr) { alert('Digite um endereço.'); return false; }
  const g = await geocode(addr);
  if (!g) { alert('Endereço não encontrado.'); return false; }
  li.dataset.lat = g.lat;
  li.dataset.lon = g.lon;
  li.querySelector('.coords').textContent = `${g.lat.toFixed(6)}, ${g.lon.toFixed(6)}`;
  if (g.display && g.display.length > addr.length) li.querySelector('.addr').value = g.display;
  renderMarkers();
  return true;
}

async function ensureAllCoordinates() {
  const items = Array.from(document.querySelectorAll('#dest-list li'));
  for (const li of items) {
    const ok = await ensureCoordinates(li);
    if (!ok) return false;
  }
  return true;
}

async function optimize() {
  const btn = document.getElementById('optimize');
  btn.disabled = true; btn.textContent = 'Otimizando...';

  const ready = await ensureAllCoordinates();
  if (!ready) { btn.disabled = false; btn.textContent = 'Otimizar rota'; return; }

  const points = [];
  document.querySelectorAll('#dest-list li').forEach((li) => {
    const lat = parseFloat(li.dataset.lat);
    const lon = parseFloat(li.dataset.lon);
    const addr = li.querySelector('.addr').value;
    if (isFinite(lat) && isFinite(lon)) points.push({ id: li.dataset.id, lat, lon, addr });
  });
  if (points.length < 2) { alert('Adicione pelo menos 2 endereços.'); btn.disabled = false; btn.textContent = 'Otimizar rota'; return; }

  const kStr = document.getElementById('k-input').value;
  const k = kStr ? Number(kStr) : undefined;

  const resp = await fetch('/optimize-route', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ points, k })
  });
  const data = await resp.json();
  if (data.error) { alert(data.error); btn.disabled = false; btn.textContent = 'Otimizar rota'; return; }

  // Reconstroi a lista na ordem ótima e desenha as polylines retornadas
  const destList = document.getElementById('dest-list');
  destList.innerHTML = '';
  layerGroup.clearLayers();
  markers = []; polylines = [];

  const palette = ['#3366cc','#dc3912','#ff9900','#109618','#990099','#0099c6','#dd4477'];

  data.clusters.forEach((c, idx) => {
    // recria lista na ordem
    c.points.forEach(p => {
      const li = addDestination(p.addr || '');
      li.dataset.id = p.id;
      li.dataset.lat = p.lat;
      li.dataset.lon = p.lon;
      li.querySelector('.coords').textContent = `${p.lat.toFixed(6)}, ${p.lon.toFixed(6)}`;
    });

    // desenha a rota pelas ruas (geometria do OSRM)
    const color = palette[idx % palette.length];
    if (Array.isArray(c.geometry) && c.geometry.length > 1) {
      const poly = L.polyline(c.geometry, { weight: 5, opacity: 0.85, color }).addTo(layerGroup);
      polylines.push(poly);
      map.fitBounds(poly.getBounds(), { padding: [20, 20] });
    }

    // marcadores numerados na ordem
    c.points.forEach((p, i) => {
      const m = L.marker([p.lat, p.lon]).addTo(layerGroup);
      m.bindTooltip(String(i + 1), { permanent: true, direction: 'top' }).openTooltip();
      markers.push(m);
    });
  });

  document.getElementById('summary').innerHTML =
    `<b>Distância total:</b> ${data.total_km} km — ` +
    `<b>ETA total:</b> ${data.total_eta_min} min — ` +
    `<b>Clusters:</b> ${data.clusters.length}`;

  btn.disabled = false; btn.textContent = 'Otimizar rota';
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
    document.getElementById('summary').textContent = '';
    clearMapLayers();
  };
}

initMap();
bindUI();
