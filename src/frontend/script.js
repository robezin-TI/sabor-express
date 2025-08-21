// --------- MAPA ---------
const map = L.map('map').setView([-23.716, -46.849], 12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors'
}).addTo(map);

let addresses = [];   // {label, coords:[lat,lon], input:HTMLInputElement}
let markers = [];
let polylines = [];

const elList = document.getElementById('addressList');
const elSummary = document.getElementById('summary');

document.getElementById('btnAdd').onclick = () => addAddressRow();
document.getElementById('btnMapClick').onclick = enableMapClick;
document.getElementById('btnOptimize').onclick = optimizeRoute;
document.getElementById('btnClear').onclick = clearAll;

function divIconNumber(n){
  return L.divIcon({
    className: 'custom-div-icon',
    html: `<div class="marker-number">${n}</div>`,
    iconSize: [30, 42],
    iconAnchor: [15, 42]
  });
}

function refreshMarkers(){
  markers.forEach(m => map.removeLayer(m));
  markers = [];
  addresses.forEach((a, i) => {
