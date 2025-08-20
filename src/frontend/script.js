let map = L.map('map').setView([-23.716, -46.849], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

let markers = [];
let polylines = [];

function addAddressField() {
    const container = document.getElementById("addresses");
    const div = document.createElement("div");
    div.className = "address-input";

    const input = document.createElement("input");
    input.type = "text";
    input.placeholder = "Digite um endereço";

    const searchBtn = document.createElement("button");
    searchBtn.innerText = "🔍";
    searchBtn.onclick = async () => {
        const res = await fetch("/api/geocode", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ address: input.value })
        });
        const data = await res.json();
        if (data.coords) {
            input.dataset.lat = data.coords[0];
            input.dataset.lon = data.coords[1];

            const marker = L.marker([data.coords[0], data.coords[1]]).addTo(map);
            markers.push(marker);
        } else {
            alert("Endereço não encontrado!");
        }
    };

    const delBtn = document.createElement("button");
    delBtn.innerText = "🗑️";
    delBtn.onclick = () => {
        container.removeChild(div);
    };

    div.appendChild(input);
    div.appendChild(searchBtn);
    div.appendChild(delBtn);
    container.appendChild(div);
}

function enableMapClick() {
    map.once('click', function(e) {
        const lat = e.latlng.lat;
        const lon = e.latlng.lng;

        const container = document.getElementById("addresses");
        const div = document.createElement("div");
        div.className = "address-input";

        const input = document.createElement("input");
        input.type = "text";
        input.value = `${lat}, ${lon}`;
        input.dataset.lat = lat;
        input.dataset.lon = lon;

        const delBtn = document.createElement("button");
        delBtn.innerText = "🗑️";
        delBtn.onclick = () => {
            container.removeChild(div);
        };

        div.appendChild(input);
        div.appendChild(delBtn);
        container.appendChild(div);

        const marker = L.marker([lat, lon]).addTo(map);
        markers.push(marker);
    });
}

async function optimizeRoute() {
    // limpa rotas antigas
    polylines.forEach(line => map.removeLayer(line));
    polylines = [];

    const addresses = [];
    document.querySelectorAll(".address-input input").forEach(input => {
        const lat = parseFloat(input.dataset.lat);
        const lon = parseFloat(input.dataset.lon);
        if (!isNaN(lat) && !isNaN(lon)) {
            addresses.push({ coords: [lat, lon] });
        }
    });

    const clusters = document.getElementById("clusters").value || 1;

    const res = await fetch("/api/optimize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ addresses, clusters })
    });

    const data = await res.json();
    if (data.error) {
        alert(data.error);
        return;
    }

    // resumo
    document.getElementById("summary").innerText =
        `Distância total: ${data.total_distance_km} km — ETA total: ${data.total_eta_min} min — Clusters: ${data.clusters}`;

    // desenha rotas
    data.routes.forEach(route => {
        route.route.geometry.forEach(segment => {
            const poly = L.polyline(segment.map(p => [p[1], p[0]]), { color: 'blue' }).addTo(map);
            polylines.push(poly);
        });
    });
}

function clearAll() {
    document.getElementById("addresses").innerHTML = "";
    document.getElementById("summary").innerText = "";

    markers.forEach(m => map.removeLayer(m));
    markers = [];

    polylines.forEach(line => map.removeLayer(line));
    polylines = [];
}
