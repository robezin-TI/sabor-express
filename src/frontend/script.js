async function optimizeRoute() {
    const addresses = [];
    document.querySelectorAll(".address-input").forEach(input => {
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
    console.log("Resultado:", data);
    // TODO: desenhar rotas no mapa com data.routes
}
