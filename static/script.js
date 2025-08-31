(() => {
  // ---------- Inicialização do mapa ----------
  const map = L.map('map').setView([-23.57, -46.63], 10);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19, attribution: '&copy; OpenStreetMap'
  }).addTo(map);

  // Estado
  let stops = []; // {id, lat, lng, name, marker}
  let routeLayer = null;
  const listEl = document.getElementById('list');

  // ---------- Helpers de marcador com letra ----------
  function letterIcon(letter){
    return L.divIcon({
      className: 'letter-marker',
      html: `<div style="
        width:32px;height:32px;border-radius:50%;
        background:#111827;color:#fff;display:grid;place-items:center;
        font-weight:800;border:2px solid #fff">${letter}</div>`,
      iconSize: [32,32],
      iconAnchor: [16,32],
      popupAnchor: [0,-28]
    });
  }

  function updateMarkerLetters(){
    stops.forEach((s, i) => {
      const letter = String.fromCharCode(65 + i);
      s.marker.setIcon(letterIcon(letter));
      s.marker.bindPopup(`<b>${letter}</b> ${s.name || `${s.lat.toFixed(5)}, ${s.lng.toFixed(5)}`}`);
    });
  }

  // ---------- Render da lista lateral ----------
  function renderList(){
    listEl.innerHTML = '';
    stops.forEach((s,i) => {
      const item = document.createElement('div');
      item.className = 'stop';
      item.dataset.id = s.id;

      const handle = document.createElement('div');
      handle.className = 'handle';
      handle.textContent = '⋮⋮';

      const badge = document.createElement('div');
      badge.className = 'badge';
      badge.textContent = String.fromCharCode(65+i);

      const input = document.createElement('input');
      input.value = s.name || `${s.lat.toFixed(5)}, ${s.lng.toFixed(5)}`;
      input.addEventListener('change', () => { s.name = input.value; updateMarkerLetters(); });

      const del = document.createElement('button');
      del.className = 'x';
      del.textContent = '×';
      del.onclick = () => removeStop(s.id);

      const left = document.createElement('div');
      left.style.display = 'flex';
      left.style.alignItems = 'center';
      left.style.gap = '8px';
      left.appendChild(handle);
      left.appendChild(badge);

      item.appendChild(left);
      item.appendChild(input);
      item.appendChild(del);

      listEl.appendChild(item);
    });

    // ativa SortableJS
    if (window.Sortable) {
      new Sortable(listEl, {
        handle: '.handle',
        animation: 150,
        onEnd: (evt) => {
          const from = evt.oldIndex;
          const to = evt.newIndex;
          if (from === to) return;
          const moved = stops.splice(from, 1)[0];
          stops.splice(to, 0, moved);
          updateMarkerLetters();
          // redesenha a rota automaticamente após reorder
          if (stops.length >= 2) {
            drawRouteFromServer();
          }
        }
      });
    }
  }

  // ---------- Adicionar / remover stops ----------
  function addStop(lat, lng, name=''){
    const id = Date.now() + '_' + Math.random();
    const marker = L.marker([lat, lng], { draggable: true, icon: letterIcon('?') }).addTo(map);
    const s = { id, lat, lng, name, marker };
    stops.push(s);

    marker.on('dragend', (e) => {
      const { lat, lng } = e.target.getLatLng();
      s.lat = lat; s.lng = lng;
      updateMarkerLetters();
      if (stops.length >= 2) drawRouteFromServer();
      renderList();
    });

    renderList();
    updateMarkerLetters();
    fitToStops();
  }

  function removeStop(id){
    const idx = stops.findIndex(s => s.id === id);
    if (idx >= 0){
      map.removeLayer(stops[idx].marker);
      stops.splice(idx, 1);
      renderList();
      updateMarkerLetters();
      if (stops.length >= 2) drawRouteFromServer();
      else removeRoute();
    }
  }

  function fitToStops(){
    if (!stops.length) return;
    const group = L.featureGroup(stops.map(s => s.marker));
    map.fitBounds(group.getBounds().pad(0.25));
  }

  // ---------- Geocoding (front-end pra UX rápido) ----------
  async function geocode(q){
    const url = `https://nominatim.openstreetmap.org/search?format=jsonv2&q=${encodeURIComponent(q)}`;
    const r = await fetch(url, { headers: { 'Accept-Language':'pt-BR', 'User-Agent': 'sabor-express' }});
    const data = await r.json();
    return data.map(d => ({ lat: +d.lat, lng: +d.lon, display: d.display_name }));
  }

  // botão adicionar (por texto)
  document.getElementById('add').onclick = async () => {
    const q = document.getElementById('search').value.trim();
    if (!q) return;
    try {
      const results = await geocode(q);
      if (!results.length) { alert('Endereço não encontrado'); return; }
      const first = results[0];
      addStop(first.lat, first.lng, q);
      document.getElementById('search').value = '';
    } catch(e){ alert('Erro na geocodificação'); }
  };

  // adicionar clicando no mapa
  map.on('click', (e) => addStop(e.latlng.lat, e.latlng.lng));

  // ---------- Roteamento & Otimização (chamando backend) ----------
  async function drawRouteFromServer(){
    if (stops.length < 2) return;
    const coords = stops.map(s => [s.lat, s.lng]);
    // chama endpoint /route para obter rota passo-a-passo (seu backend deve repassar OSRM)
    try {
      const res = await fetch('/route', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ coords })
      });
      const data = await res.json();
      renderRouteAndDirections(data);
    } catch(err){
      console.error(err);
      alert('Erro ao obter rota');
    }
  }

  async function optimizeRoute(){
    if (stops.length < 3) { drawRouteFromServer(); return; }
    const coords = stops.map(s => [s.lat, s.lng]);
    try {
      const res = await fetch('/optimize', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ coords })
      });
      const data = await res.json();
      // o endpoint /optimize (trip) retornará trips[0] e waypoints com waypoint_index
      if (data.code && data.code !== 'Ok') { alert('OSRM: sem solução'); return; }

      // reordena stops conforme waypoint_index (preserva 1º e último se solicitado pelo backend)
      const order = (data.waypoints || [])
        .slice()
        .sort((a,b) => a.waypoint_index - b.waypoint_index)
        .map(w => w.waypoint_index);

      // se retornou order, reordena stops array
      if (order && order.length === stops.length) {
        stops = order.map(i => stops[i]);
        // atualiza marcadores e lista
        renderList();
        updateMarkerLetters();
      }

      // desenha a rota usando geometry do trip (trips[0].geometry)
      renderRouteAndDirections(data);
    } catch(err){
      console.error(err);
      alert('Erro ao otimizar rota');
    }
  }

  // liga botões
  document.getElementById('route').onclick = drawRouteFromServer;
  document.getElementById('optimize').onclick = optimizeRoute;

  // ---------- Renderiza rota e painel de instruções ----------
  function removeRoute(){
    if (routeLayer) {
      map.removeLayer(routeLayer);
      routeLayer = null;
    }
    const box = document.querySelector('.directions-box');
    if (box) box.remove();
  }

  function renderRouteAndDirections(osrmJson){
    removeRoute();

    // OSRM: pode retornar routes[] (route) ou trips[] (trip)
    let route = null;
    if (osrmJson.routes && osrmJson.routes.length) route = osrmJson.routes[0];
    else if (osrmJson.trips && osrmJson.trips.length) route = osrmJson.trips[0];
    else {
      console.warn('Resposta OSRM inesperada', osrmJson);
      return;
    }

    // geometria
    const geom = route.geometry; // geojson (se seu backend definiu geometries=geojson)
    if (geom) {
      routeLayer = L.geoJSON(geom, { style: { color: '#2563eb', weight: 5, opacity: 0.8 } }).addTo(map);
      map.fitBounds(routeLayer.getBounds().pad(0.15));
    }

    // summary
    const distance_m = route.distance || (route.summary && route.summary.distance) || 0;
    const duration_s = route.duration || (route.summary && route.summary.duration) || 0;

    // passos: cada leg tem steps
    const legs = route.legs || [];
    const steps = legs.flatMap(leg => leg.steps || []);

    // cria caixa de direções (estética similar à print)
    const existing = document.querySelector('.directions-box');
    if (existing) existing.remove();

    const box = document.createElement('div');
    box.className = 'directions-box';
    const title = document.createElement('h4');
    title.innerText = route.name || 'Rota';
    box.appendChild(title);

    const summary = document.createElement('div');
    summary.className = 'directions-summary';
    const km = (distance_m / 1000).toFixed(2);
    const min = Math.round(duration_s / 60);
    summary.innerText = `${km} km, ${min} min`;
    box.appendChild(summary);

    // percorre passos e cria linhas
    steps.forEach((s, idx) => {
      const row = document.createElement('div');
      row.className = 'direction-step';

      const ico = document.createElement('div');
      ico.className = 'step-ico';
      // tenta extrair uma letra curta do tipo de manobra
      const typ = s.maneuver && s.maneuver.type ? s.maneuver.type[0].toUpperCase() : '→';
      ico.innerText = typ;

      const txt = document.createElement('div');
      txt.className = 'step-text';
      // OSRM pode não ter 'instruction' textual direto; montamos uma frase:
      const road = s.name || '';
      const mod = (s.maneuver && s.maneuver.modifier) ? ` ${s.maneuver.modifier}` : '';
      const human = s.maneuver && s.maneuver.instruction ? s.maneuver.instruction :
                    `${(s.maneuver && s.maneuver.type) || 'Seguir'}${mod} ${road}`.trim();
      txt.innerText = human;

      const meta = document.createElement('div');
      meta.className = 'step-meta';
      const d = (s.distance !== undefined) ? `${Math.round(s.distance)} m` : '';
      meta.innerText = d;

      row.appendChild(ico);
      row.appendChild(txt);
      row.appendChild(meta);
      box.appendChild(row);
    });

    document.body.appendChild(box);
  }

  // ---------- Limpar tudo ----------
  document.getElementById('clear').onclick = () => {
    stops.forEach(s => map.removeLayer(s.marker));
    stops = [];
    renderList();
    removeRoute();
  };

  // ---------- inicial render ----------
  renderList();

})();
