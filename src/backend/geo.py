import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

def geocode_address(address):
    """Converte endereço em coordenadas (lat, lon)"""
    params = {"q": address, "format": "json", "limit": 1}
    resp = requests.get(NOMINATIM_URL, params=params, headers={"User-Agent": "route-ai-app"})
    if resp.status_code == 200 and resp.json():
        data = resp.json()[0]
        return [float(data["lat"]), float(data["lon"])]
    return None
