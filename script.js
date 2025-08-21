let map = L.map('map').setView([-23.55, -46.63], 12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

let markers = [];
let polyline = null;

function numberIcon(n) {
  return L.divIcon({ className: 'num-icon',
    html: `<div style="background:#2b7cff;color:white;border-radius:14px;
      width:28px;height:28px;display:flex;align-items:center;justify-content:center;
      font-weight:bold">${n}</div>` });
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
}

document.getElementById('addAddressBtn').onclick = async ()=>{
  const addr = prompt("Digite endereço:");
  if (addr) await addAddress(addr);
};

document.getElementById('clickModeBtn').onclick = ()=>{
  map.once('click', e=>{
    const m = L.marker([e.latlng.lat,e.latlng.lng],{icon:numberIcon(markers.length+1)}).addTo(map);
    markers.push({lat:e.latlng.lat, lon:e.latlng.lng, label:"Ponto", marker:m});
  });
};

document.getElementById('optBtn').onclick = async ()=>{
  const points = markers.map(m=>({lat:m.lat, lon:m.lon, label:m.label}));
  const res = await fetch('/optimize',{
    method:'POST', headers:{'Content-Type':'application/json'},
    body:JSON.stringify({points})
  });
  const d = await res.json();
  if (polyline) map.removeLayer(polyline);
  polyline = L.polyline(d.route, {color:'red'}).addTo(map);
  map.fitBounds(polyline.getBounds());
};

document.getElementById('clearBtn').onclick = ()=>{
  markers.forEach(m=>map.removeLayer(m.marker));
  markers=[]; if(polyline){map.removeLayer(polyline); polyline=null;}
};
