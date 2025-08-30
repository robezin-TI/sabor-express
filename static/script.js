async function testGeocode() {
  const res = await fetch("/api/geocode", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({address: "Av. Paulista"})
  });
  document.getElementById("output").textContent = JSON.stringify(await res.json(), null, 2);
}

async function testRoute() {
  const graph = {
    "(0,0)": [[[0,1], 1], [[1,0], 1]],
    "(0,1)": [[[1,1], 1]],
    "(1,0)": [[[1,1], 1]],
    "(1,1)": []
  };
  const res = await fetch("/api/route", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({start: [0,0], end: [1,1], graph})
  });
  document.getElementById("output").textContent = JSON.stringify(await res.json(), null, 2);
}

async function testCluster() {
  const res = await fetch("/api/cluster", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({points: [[1,2],[2,3],[10,10],[12,11]], k: 2})
  });
  document.getElementById("output").textContent = JSON.stringify(await res.json(), null, 2);
}

async function testML() {
  await fetch("/api/train", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({features: [[1],[2],[3]], targets: [2,4,6]})
  });

  const res = await fetch("/api/predict", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({features: [4]})
  });
  document.getElementById("output").textContent = JSON.stringify(await res.json(), null, 2);
}
