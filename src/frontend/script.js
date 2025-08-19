let map = L.map('map').setView([-23.7, -46.85], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

let markers = [];
let polylines = [];

function genId() {
  return Math.random().toString(36).substr(2, 9);
}

function renumber() {
  document.querySelectorAll('#dest-list li').forEach((li, i) => {
    li.querySelector('.badge').textContent = i + 1;
  });
}

function addDestination(address = '') {
  const li = document.createElement('li');
  li.draggable = true;
  li.dataset.id = genId();

  li.innerHTML = `
    <span class="badge">#</span>
    <input class="addr" type="text" placeholder="Digite um endereço" value="${address}">
    <button class="geocode">🔍</button>
    <button class="remove">🗑️</button>
    <div class="coords"></div>
  `;

  li.querySelector('.remove').onclick = () => { li.remove(); renumber(); };

  li.querySelector('.geocode').onclick = async () => {
    const addr = li.querySelector('.addr').value;
    if (!addr) return;
    const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(addr)}&format=json&limit=1`;
    const res = await fetch(url);
    const data = await res.json();
    if (data.length > 0) {
      const { lat, lon, display_name } = data[0];
      li.dataset.lat = lat;
      li.dataset.lon = lon;
      li.querySelector('.coords').textContent = `${lat}, ${lon}`;
      li.querySelector('.addr').value = display_name;
      renderMarkers();
    } else {
      alert("Endereço não encontrado!");
    }
  };

  document.getElementById('dest-list').appendChild(li);
  renumber();
  return li;
}

function renderMarkers() {
  markers.forEach(m => map.removeLayer(m));
  markers = [];
  polylines.forEach(p => map.removeLayer(p));
  polylines = [];

  document.querySelectorAll('#dest-list li').forEach((li, i) => {
    if (li.dataset.lat && li.dataset.lon) {
      const lat = parseFloat(li.dataset.lat);
      const lon = parseFloat(li.dataset.lon);
      const marker = L.marker([lat, lon]).addTo(map).bindPopup(li.querySelector('.addr').value);
      markers.push(marker);
    }
  });
}

async function optimize() {
  const points = [];
  document.querySelectorAll('#dest-list li').forEach(li => {
    const lat = parseFloat(li.dataset.lat);
    const lon = parseFloat(li.dataset.lon);
    if (isFinite(lat) && isFinite(lon)) {
      points.push({ id: li.dataset.id, lat, lon, addr: li.querySelector('.addr').value });
    }
  });

  if (points.length < 2) {
    alert('Adicione pelo menos 2 endereços.');
    return;
  }

  const kStr = document.getElementById('k-input').value;
  const k = kStr && kStr !== "auto" ? Number(kStr) : undefined;

  const resp = await fetch('/optimize-route', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ points, k })
  });
  const data = await resp.json();
  if (data.error) { alert(data.error); return; }

  // Reordena lista
  const destList = document.getElementById('dest-list');
  destList.innerHTML = '';

  data.clusters.forEach((c) => {
    c.points.forEach((p, idx) => {
      const li = addDestination(p.addr || "");
      li.dataset.id = p.id;
      li.dataset.lat = p.lat;
      li.dataset.lon = p.lon;
      li.querySelector('.coords').textContent = `${p.lat.toFixed(6)}, ${p.lon.toFixed(6)}`;
      li.querySelector('.badge').textContent = String(idx + 1);
    });

    if (c.geometry && c.geometry.length > 1) {
      const latlngs = c.geometry.map(([lon, lat]) => [lat, lon]);
      const poly = L.polyline(latlngs, {color: 'blue'}).addTo(map);
      polylines.push(poly);
    }
  });

  document.getElementById('summary').innerHTML =
    `<b>Distância total:</b> ${data.total_km} km — ` +
    `<b>ETA total:</b> ${data.total_eta_min} min — ` +
    `<b>Clusters:</b> ${data.clusters.length}`;

  renderMarkers();
}
