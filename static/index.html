// Inicializa o mapa
const map = L.map('map').setView([-23.55052, -46.633308], 12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

let markers = [];
let routeControl = null;
let routeLine = null;
let vehicleMarker = null;
let animationInterval = null;

// Inicializa Sortable para drag & drop
const listEl = document.getElementById('list');
const sortable = Sortable.create(listEl, {
  animation: 150,
  onEnd: function() {
    // Reordena marcadores conforme lista
    const newOrder = [];
    listEl.querySelectorAll('.stop').forEach(item => {
      const index = parseInt(item.dataset.index);
      newOrder.push(markers[index]);
    });
    markers = newOrder;
    updateRoute();
    // Atualiza dataset e labels
    markers.forEach((m, i) => {
      m.bindPopup(listEl.children[i].querySelector('input').value);
      listEl.children[i].dataset.index = i;
    });
  }
});

// Adiciona item na lista lateral
function addListItem(label) {
  const div = document.createElement('div');
  div.className = 'stop';
  div.dataset.index = markers.length - 1;

  div.innerHTML = `
    <div class="handle">≡</div>
    <input value="${label}" />
    <button class="x">×</button>
  `;
  listEl.appendChild(div);

  const inputEl = div.querySelector('input');
  inputEl.addEventListener('input', () => {
    const idx = parseInt(div.dataset.index);
    markers[idx].bindPopup(inputEl.value);
  });

  // Botão remover
  div.querySelector('.x').addEventListener('click', () => {
    const idx = parseInt(div.dataset.index);
    map.removeLayer(markers[idx]);
    markers.splice(idx, 1);
    div.remove();
    listEl.querySelectorAll('.stop').forEach((el, i) => el.dataset.index = i);
    updateRoute();
  });
}

// Adiciona marcador e item na lista
function addMarker(latlng, label) {
  const marker = L.marker(latlng, { draggable: true })
    .addTo(map)
    .bindPopup(label)
    .openPopup();

  marker.on('dragend', updateRoute);
  markers.push(marker);
  addListItem(label);
  updateRoute();
}

// Limpar tudo
function clearMarkers() {
  markers.forEach(m => map.removeLayer(m));
  markers = [];
  if (routeControl) { map.removeControl(routeControl); routeControl = null; }
  if (routeLine) { map.removeLayer(routeLine); routeLine = null; }
  if (vehicleMarker) { map.removeLayer(vehicleMarker); vehicleMarker = null; }
  if (animationInterval) { clearInterval(animationInterval); animationInterval = null; }
  listEl.innerHTML = '';
  document.getElementById('dir-steps').innerHTML = '';
  document.getElementById('directions').classList.add('hidden');
}

// Geocoding via Nominatim
async function geocode(address) {
  const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}`;
  const res = await fetch(url);
  const data = await res.json();
  if (data.length > 0) return [parseFloat(data[0].lat), parseFloat(data[0].lon)];
  return null;
}

// Atualiza rota e painel
function updateRoute() {
  if (markers.length < 2) {
    if (routeControl) map.removeControl(routeControl);
    if (routeLine) { map.removeLayer(routeLine); routeLine = null; }
    document.getElementById('directions').classList.add('hidden');
    document.getElementById('dir-steps').innerHTML = '';
    return;
  }

  const waypoints = markers.map(m => L.latLng(m.getLatLng()));
  if (routeControl) map.removeControl(routeControl);
  if (routeLine) map.removeLayer(routeLine);

  routeControl = L.Routing.control({
    waypoints,
    lineOptions: { styles: [{ color: '#2563eb', weight: 5 }] },
    addWaypoints: false,
    draggableWaypoints: false,
    fitSelectedRoutes: true,
    show: false
  }).addTo(map);

  routeControl.on('routesfound', function(e) {
    const route = e.routes[0];
    const summary = `${(route.summary.totalDistance/1000).toFixed(2)} km, ${(route.summary.totalTime/60).toFixed(0)} min`;
    document.getElementById('dir-summary').innerText = summary;

    const stepsContainer = document.getElementById('dir-steps');
    stepsContainer.innerHTML = '';
    route.instructions.forEach((step, i) => {
      const li = document.createElement('li');
      li.className = 'dir-step';
      li.innerHTML = `<div class="dir-ico">${i+1}</div><div class="dir-txt">${step.text}</div>`;
      stepsContainer.appendChild(li);
    });
    document.getElementById('directions').classList.remove('hidden');

    const latlngs = route.coordinates.map(c => [c.lat, c.lng]);
    routeLine = L.polyline(latlngs, { color: '#2563eb', weight: 5 }).addTo(map);
    map.fitBounds(routeLine.getBounds(), { padding: [50,50] });
  });
}

// Animação do veículo
function animateVehicle(routeCoords, speed = 100) {
  if (vehicleMarker) map.removeLayer(vehicleMarker);
  if (animationInterval) clearInterval(animationInterval);

  let index = 0;
  vehicleMarker = L.marker(routeCoords[0], { icon: L.icon({ iconUrl: 'https://cdn-icons-png.flaticon.com/512/684/684908.png', iconSize: [32,32] }) }).addTo(map);

  animationInterval = setInterval(() => {
    index++;
    if (index >= routeCoords.length) { clearInterval(animationInterval); animationInterval = null; return; }
    vehicleMarker.setLatLng(routeCoords[index]);
    map.panTo(routeCoords[index]);
  }, speed);
}

// Eventos
map.on('click', e => addMarker(e.latlng, `Ponto ${markers.length + 1}`));

document.getElementById('add').addEventListener('click', async () => {
  const input = document.getElementById('search');
  const address = input.value.trim();
  if (!address) return;
  const latlng = await geocode(address);
  if (latlng) {
    addMarker(latlng, address);
    map.setView(latlng, 14);
    input.value = '';
  } else alert('Endereço não encontrado!');
});

document.getElementById('clear').addEventListener('click', clearMarkers);
document.getElementById('close-directions').addEventListener('click', () => {
  document.getElementById('directions').classList.add('hidden');
});
document.getElementById('route').addEventListener('click', updateRoute);

document.getElementById('optimize').addEventListener('click', async () => {
  if (markers.length < 3) return;

  const coords = markers.map(m => `${m.getLatLng().lng},${m.getLatLng().lat}`).join(';');
  const url = `https://router.project-osrm.org/trip/v1/driving/${coords}?source=first&roundtrip=false&overview=full&geometries=geojson`;

  const res = await fetch(url);
  const data = await res.json();

  if (data.code === 'Ok') {
    const order = data.trips[0].waypoint_order;
    const newMarkers = order.map(i => markers[i]);
    markers.forEach(m => map.removeLayer(m));
    markers = [];
    listEl.innerHTML = '';

    newMarkers.forEach((m, idx) => {
      m.addTo(map);
      m.bindPopup(`Ponto ${idx+1}`).openPopup();
      markers.push(m);
      addListItem(m.getPopup().getContent());
    });

    const routeCoords = data.trips[0].geometry.coordinates.map(c => [c[1], c[0]]);
    if (routeLine) map.removeLayer(routeLine);
    routeLine = L.polyline(routeCoords, { color: '#2563eb', weight: 5 }).addTo(map);
    map.fitBounds(routeLine.getBounds(), { padding: [50,50] });

    updateRoute();
    animateVehicle(routeCoords, 200);
  } else alert('Não foi possível otimizar a rota!');
});
