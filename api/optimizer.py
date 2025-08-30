import requests

def optimize_route_osrm(coords):
    """Chama OSRM para otimizar rota (TSP simplificado)."""
    base_url = "http://router.project-osrm.org/trip/v1/driving/"
    coord_str = ";".join([f"{lon},{lat}" for lat, lon in coords])
    url = f"{base_url}{coord_str}?roundtrip=true&source=first&steps=true&geometries=geojson"
    
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    return None

def route_osrm(coords):
    """Traça rota simples entre os pontos (sem otimizar)."""
    base_url = "http://router.project-osrm.org/route/v1/driving/"
    coord_str = ";".join([f"{lon},{lat}" for lat, lon in coords])
    url = f"{base_url}{coord_str}?steps=true&geometries=geojson"
    
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    return None
