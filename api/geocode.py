import requests

def get_coordinates(address):
    """Geocodifica um endereço usando Nominatim (OSM)."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1}
    response = requests.get(url, params=params, headers={"User-Agent": "sabor-express"})
    
    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return float(data["lat"]), float(data["lon"])
    return None, None
