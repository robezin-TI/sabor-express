import requests

def geocode_address(address: str):
    """
    Consulta Nominatim (OSM) para obter coordenadas de um endereço.
    Retorna: {"lat": float, "lon": float} ou {"error": "..."}
    """
    if not address or not address.strip():
        return {"error": "Endereço vazio"}

    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1}
    try:
        r = requests.get(url, params=params, headers={"User-Agent": "sabor-express"})
        r.raise_for_status()
        js = r.json()
        if js:
            data = js[0]
            return {"lat": float(data["lat"]), "lon": float(data["lon"])}
        return {"error": "Endereço não encontrado"}
    except Exception as e:
        return {"error": f"Falha na geocodificação: {e}"}
