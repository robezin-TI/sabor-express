import requests

def geocode_address(address):
    """Consulta Nominatim para obter coordenadas de um endereço"""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1}
    r = requests.get(url, params=params, headers={"User-Agent": "sabor-express"})
    if r.status_code == 200 and r.json():
        data = r.json()[0]
        return {"lat": float(data["lat"]), "lon": float(data["lon"])}
    return {"error": "Endereço não encontrado"}
