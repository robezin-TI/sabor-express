import kmeans from "https://cdn.jsdelivr.net/npm/ml-kmeans/+esm";

const map = L.map("map").setView([-23.55, -46.63], 13);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors"
}).addTo(map);

let points = [];
let routeLayer;

// Função auxiliar para criar marcador
function createMarker(lat, lng, label) {
  const marker = L.marker([lat, lng], { draggable: false }).addTo(map);
  marker.bindPopup(label);
  return marker;
}

// Adicionar ponto manualmente (input)
document.getElementById("addPointBtn").addEventListener("click", () => {
  const input = document.getElementById("addressInput").value.trim();
  if (!input) return;

  fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(input)}`)
    .then(res => res.json())
    .then(data => {
      if (data.length === 0) {
        alert("Endereço não encontrado!");
        return;
      }
      const { lat, lon } = data[0];
      addPoint(parseFloat(lat), parseFloat(lon), input);
    });
});

// Adicionar ponto clicando no mapa
map.on("click", e => {
  addPoint(e.latlng.lat, e.latlng.lng, `Ponto ${points.length + 1}`);
});

// Função para adicionar ponto
function addPoint(lat, lng, label) {
  const marker = createMarker(lat, lng, label);
  const point = { lat, lng, label, marker };
  points.push(point);
  renderPointsList();
}

// Renderizar lista lateral de pontos
function renderPointsList() {
  const list = document.getElementById("pointsList");
  list.innerHTML = "";
  points.forEach((p, i) => {
    const item = document.createElement("div");
    item.className = "point-item";
    item.textContent = p.label;
    const delBtn = document.createElement("button");
    delBtn.textContent = "x";
    delBtn.onclick = () => {
      map.removeLayer(p.marker);
      points.splice(i, 1);
      renderPointsList();
    };
    item.appendChild(delBtn);
    list.appendChild(item);
  });

  Sortable.create(list, {
    animation: 150,
    onEnd: (evt) => {
      const moved = points.splice(evt.oldIndex, 1)[0];
      points.splice(evt.newIndex, 0, moved);
    }
  });
}

// Traçar rota
document.getElementById("routeBtn").addEventListener("click", () => {
  if (points.length < 2) {
    alert("Adicione pelo menos 2 pontos!");
    return;
  }

  const coords = points.map(p => `${p.lng},${p.lat}`).join(";");
  fetch(`https://router.project-osrm.org/route/v1/driving/${coords}?overview=full&geometries=geojson&steps=true`)
    .then(res => res.json())
    .then(data => {
      if (routeLayer) map.removeLayer(routeLayer);
      const route = data.routes[0];
      routeLayer = L.geoJSON(route.geometry).addTo(map);
      map.fitBounds(routeLayer.getBounds());
    });
});

// Limpar tudo
document.getElementById("clearBtn").addEventListener("click", () => {
  points.forEach(p => map.removeLayer(p.marker));
  points = [];
  if (routeLayer) map.removeLayer(routeLayer);
  renderPointsList();
});

// Função auxiliar para gerar cor
function getClusterColor(clusterId) {
  const colors = ["red", "green", "blue", "purple", "orange"];
  return colors[clusterId % colors.length];
}

// Agrupar com K-Means
document.getElementById("clusterBtn").addEventListener("click", () => {
  if (points.length < 2) {
    alert("Adicione pelo menos 2 pontos!");
    return;
  }

  const coords = points.map(p => [p.lat, p.lng]);
  const k = 2; // pode trocar por 3, 4 etc.

  const result = kmeans(coords, k);

  result.clusters.forEach((clusterId, i) => {
    const color = getClusterColor(clusterId);
    points[i].marker.setIcon(L.icon({
      iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${color}.png`,
      shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png`,
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41]
    }));
  });

  alert(`Pontos agrupados em ${k} clusters!`);
});
