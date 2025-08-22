let map = L.map('map').setView([-23.55, -46.63], 12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap'
}).addTo(map);

let markers = [];
let polyline = null;
let clickMode = false;

function numberIcon(n) {
  return L.divIcon({ className: 'num-icon',
    html: `<div style="background:#2b7cff;color:white;border-radius:14px;
      width:26px;height:26px;display:flex;align-items:center;justify-content:center;
      font-weight:bold">${n}</div>` });
}

function refreshList() {
  const list = document.getElementById('addressList');
  list.innerHTML = "";
  markers.forEach((m, i)=>{
    const li = document.createElement("li");
    li.innerText = `${i+1}. ${m.label}`;
    list.appendChild(li);
  });
}

async function addAddress(addr) {
  const res = await fetch('/geocode', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body:JSON.stringify({address:addr})
  });
  const d = await res.json();
  if (!res.ok) { alert("Erro: " + d.error); return; }
  const m = L.marker([d.lat,d.lon],{icon:numberIcon(markers.length+1)}).addTo(map);
  markers.push({lat:d.lat, lon:d.lon, label:d.label, marker:m});
  refreshList();
}

document.getElementById('addAddressBtn').onclick = async ()=>{
  const addr = document.getElementById('addressInput').value;
  if (addr) {
    await addAddress(addr);
    document.getElementById('addressInput').value = "";
  }
};

document.getElementById('clickModeBtn').onclick = ()=>{
  clickMode = true;
  alert("Clique no mapa para adicionar um ponto.");
};

map.on('click', e=>{
  if (!clickMode) return;
  clickMode = false;
  const m = L.marker([e.latlng.lat,e.latlng.lng],{icon:numberIcon(markers.length+1)}).addTo(map);
  markers.push({lat:e.latlng.lat, lon:e.latlng.lng, label:"Ponto", marker:m});
  refreshList();
});

document.getElementById('optBtn').onclick = async ()=>{
  const points = markers.map(m=>({lat:m.lat, lon:m.lon, label:m.label}));
  const res = await fetch('/optimize',{
    method:'POST', headers:{'Content-Type':'application/json'},
    body:JSON.stringify({points})
  });
  const d = await res.json();
  if (polyline) map.removeLayer(polyline);

  markers.forEach(m=>map.removeLayer(m.marker));
  markers=[];
  d.ordered_points.forEach((p,i)=>{
    const m = L.marker([p.lat,p.lon],{icon:numberIcon(i+1)}).addTo(map);
    markers.push({lat:p.lat, lon:p.lon, label:p.label, marker:m});
  });
  refreshList();

  polyline = L.polyline(d.route, {color:'red'}).addTo(map);
  map.fitBounds(polyline.getBounds());
};

document.getElementById('clearBtn').onclick = ()=>{
  markers.forEach(m=>map.removeLayer(m.marker));
  markers=[]; refreshList();
  if(polyline){map.removeLayer(polyline); polyline=null;}
};
