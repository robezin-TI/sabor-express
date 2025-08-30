async function simulate() {
  const addresses = ["Rua A", "Rua B", "Rua C", "Rua D"];
  const coords = [];

  for (let addr of addresses) {
    let res = await fetch("/api/geocode", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({address: addr})
    });
    coords.push(await res.json());
  }

  let clusterRes = await fetch("/api/cluster", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({points: coords, n_clusters: 2})
  });
  let clustered = await clusterRes.json();

  let optRes = await fetch("/api/optimize", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({points: clustered.points})
  });
  let path = await optRes.json();

  document.getElementById("output").innerText = JSON.stringify({
    clustered,
    path
  }, null, 2);
}
