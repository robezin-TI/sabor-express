import requests

USER_AGENT = "sabor-express-route-optimizer/1.0"

def geocode_address(address: str):
    """
    Converte um endereço em [lat, lon] usando Nominatim (OSM).
    """
    if not address:
        return None
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1}
    r = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=20)
    if r.ok and r.json():
        j = r.json()[0]
        return [float(j["lat"]), float(j["lon"])]
    return None
