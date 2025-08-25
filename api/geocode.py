import requests

def geocode_address(address):
    """Usa Nominatim (OpenStreetMap) para obter coordenadas de um endereço"""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1}
    response = requests.get(url, params=params)

    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return {"lat": float(data["lat"]), "lon": float(data["lon"])}
    return {"error": "Endereço não encontrado"}
