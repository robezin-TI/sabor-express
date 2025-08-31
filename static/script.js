(() => {
  // ---------- MAPA ----------
  const map = L.map('map', { zoomControl: true }).setView([-23.57, -46.63], 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
  }).addTo(map);

  // ---------- ESTADO ----------
  let stops = [];          // {id, name, lat, lng, marker}
  const listEl = document.getElementById('list');
  const dirPanel = document.getElementById('directions');
  const dirSummaryEl = document.getElementById('dir-summary');
  const dirStepsEl = document.getElementById('dir-steps');

  // ---------- UI HELPERS ----------
  function letterIcon(letter) {
    return L.divIcon({
      className: 'letter-marker',
      html: `
        <div class="pin">
          <div class="pin-inner">${letter}</div>
        </div>`,
      iconSize: [34, 46],
      iconAnchor: [17, 46],
      popupAnchor: [0, -40]
    });
  }

  function updateMarkerLetters(){
    stops.forEach((s,i) => {
      const letter = String.fromCharCode(65+i);
      s.marker.setIcon(letterIcon(letter));
      s.marker.bindPopup(`<b>${letter}</b> ${s.name || `${s.lat.toFixed(5)}, ${s.lng.toFixed(5)}`}`);
    });
  }

  function fitToStops(){
    if(!stops.length) return;
    const group = L.featureGroup(stops.map(s => s.marker));
    map.fitBounds(group.getBounds().pad(0.25));
  }

  function removeStop(id){
    const idx = stops.findIndex(s => s.id === id);
    if (idx >= 0) {
      map.removeLayer(stops[idx].marker);
      stops.splice(idx,1);
      renderList();
      updateMarkerLetters();
      clearRoute();
    }
  }

  function addStop(lat,lng,name=''){
    const id = Date.now()+'_'+Math.random();
    const marker = L.marker([lat,lng], { draggable:true, icon:letterIcon('?') }).addTo(map);
    const s = { id, name, lat, lng, marker };
    stops.push(s);

    marker.on('dragend', (e) => {
      const { lat, lng } = e.target.getLatLng();
      s.lat = lat; s.lng = lng;
      updateMarkerLetters();
      drawRoute(); // atualiza se já tiver rota
    });

    renderList();
    updateMarkerLetters();
    fitToStops();
  }

  // click no mapa para adicionar ponto
  map.on('click', (e) => addStop(e.latlng.lat, e.latlng.lng));

  // ---------- LISTA (Drag & Drop) ----------
  function renderList(){
    listEl.innerHTML = '';
    stops.forEach((s,i) => {
      const item = document.createElement('div');
      item.className = 'stop';
      item.dataset.id = s.id;

      const handle = document.createElement('div');
      handle.className = 'handle';
      handle.title = 'Arrastar para reordenar';
      handle.textContent = '⋮⋮';

      const badge = document.createElement('div');
      badge.className = 'badge';
      badge.textContent = String.fromCharCode(65+i);

      const input = document.createElement('input');
      input.value = s.name || `${s.lat.toFixed(5)}, ${s.lng.toFixed(5)}`;
      input.placeholder = 'Endereço ou nome';
      input.addEventListener('change', () => { s.name = input.value; updateMarkerLetters(); });

      const left = document.createElement('div');
      left.className = 'left';
      left.appendChild(handle);
      left.appendChild(badge);

      const del = document.createElement('button');
      del.className = 'x';
      del.textContent = '×';
      del.onclick = () => removeStop(s.id);

      item.appendChild(left);
      item.appendChild(input);
      item.appendChild(del);
      listEl.appendChild(item);
    });

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
          drawRoute();
        }
      });
    }
  }

  // ---------- GEOCODIFICAÇÃO ----------
  async function geocode(q){
    const url = `https://nominatim.openstreetmap.org/search?format=jsonv2&q=${encodeURIComponent(q)}`;
    const r = await fetch(url, { headers: { 'Accept-Language':'pt-BR' }});
    const data = await r.json();
    return data.map(d => ({ lat: +d.lat, lng: +d.lon, display: d.display_name }));
  }

  const input = document.getElementById('search');
  document.getElementById('add').onclick = async () => {
    const q = input.value.trim();
    if(!q) return;
    try{
      const [first] = await geocode(q);
      if(!first) { alert('Endereço não encontrado'); return; }
      addStop(first.lat, first.lng, q);
      input.value = '';
    }catch(err){ alert('Erro ao buscar endereço.'); }
  };

  // ---------- ROTA (OSRM) ----------
  let routeLayer = null;

  function clearRoute(){
    if(routeLayer){ map.removeLayer(routeLayer); routeLayer = null; }
    hideDirections();
  }

  function hideDirections(){
    dirPanel.classList.add('hidden');
    dirStepsEl.innerHTML = '';
    dirSummaryEl.textContent = '—';
  }
  function showDirections(){ dirPanel.classList.remove('hidden'); }

  document.getElementById('close-directions').onclick = hideDirections;

  function formatDuration(sec){
    const m = Math.round(sec/60);
    if (m < 60) return `${m} min`;
    const h = Math.floor(m/60);
    const mm = m % 60;
    return `${h} h ${mm} min`;
  }

  function stepIcon(type) {
    // ícones simples baseados em "type" do OSRM
    const map = {
      'turn-left': '↰','turn-right':'↱','uturn':'⟲','continue':'↑',
      'depart':'A','arrive':'B','roundabout':'⟳','merge':'⇶',
      'on ramp':'↗','off ramp':'↘'
    };
    return map[type] || '→';
  }

  async function drawRoute(){
    if (stops.length < 2){
      clearRoute();
      return;
    }

    const coords = stops.map(s => `${s.lng},${s.lat}`).join(';');
    const url = `https://router.project-osrm.org/route/v1/driving/${coords}?overview=full&geometries=geojson&steps=true&annotations=distance,duration`;
    const r = await fetch(url);
    const data = await r.json();

    if(data.code !== 'Ok' || !data.routes?.length){
      alert('OSRM não retornou rota.');
      return;
    }

    const route = data.routes[0];
    const line = route.geometry;

    if (routeLayer) map.removeLayer(routeLayer);
    routeLayer = L.geoJSON(line, { style: { weight: 6, opacity: 0.9 } }).addTo(map);
    map.fitBounds(routeLayer.getBounds().pad(0.2));

    // Painel de instruções custom
    const km = (route.distance/1000).toFixed(1);
    const dur = formatDuration(route.duration);
    dirSummaryEl.textContent = `${km} km • ${dur}`;
    dirStepsEl.innerHTML = '';

    // OSRM steps por "legs"
    route.legs.forEach((leg, idxLeg) => {
      leg.steps.forEach((st) => {
        const li = document.createElement('li');
        li.className = 'dir-step';

        const icon = document.createElement('div');
        icon.className = 'dir-ico';
        icon.textContent = stepIcon(st.maneuver.type);

        const txt = document.createElement('div');
        txt.className = 'dir-txt';
        const dist = (st.distance/1000);
        const niceDist = dist < 1 ? `${Math.round(st.distance)} m` : `${dist.toFixed(1)} km`;
        txt.innerHTML = `
          <div class="dir-inst">${st.name ? `Siga por <b>${st.name}</b>` : 'Continue'}</div>
          <div class="dir-minor">${niceDist}</div>
        `;

        li.appendChild(icon);
        li.appendChild(txt);
        dirStepsEl.appendChild(li);
      });

      // marca chegada da perna
      if (idxLeg < route.legs.length) {
        const li = document.createElement('li');
        li.className = 'dir-step arrive';
        li.innerHTML = `<div class="dir-ico">B</div><div class="dir-txt"><div class="dir-inst">Chegada ao ponto ${String.fromCharCode(65+idxLeg+1)}</div></div>`;
        dirStepsEl.appendChild(li);
      }
    });

    showDirections();
  }

  document.getElementById('route').onclick = drawRoute;

  // ---------- OTIMIZAÇÃO DE ORDEM (OSRM Trip) ----------
  async function optimize(){
    if(stops.length < 3){ drawRoute(); return; }
    const coords = stops.map(s => `${s.lng},${s.lat}`).join(';');
    const url = `https://router.project-osrm.org/trip/v1/driving/${coords}?source=first&destination=last&roundtrip=false&geometries=geojson`;
    const r = await fetch(url);
    const data = await r.json();
    if(data.code !== 'Ok'){ alert('OSRM não retornou solução.'); return; }

    // a API retorna o order dos waypoints (waypoint_index)
    const order = data.waypoints
      .slice()
      .sort((a,b)=>a.waypoint_index-b.waypoint_index)
      .map(w=>w.trips_index === 0 ? w.waypoint_index : w.waypoint_index);

    stops = order.map(i => stops[i]);
    renderList();
    updateMarkerLetters();
    drawRoute();
  }
  document.getElementById('optimize').onclick = optimize;

  // ---------- LIMPAR ----------
  document.getElementById('clear').onclick = () => {
    stops.forEach(s => map.removeLayer(s.marker));
    stops = [];
    renderList();
    clearRoute();
  };

  // ---------- INIT ----------
  renderList();
})();
