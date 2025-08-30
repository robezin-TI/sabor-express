# api/geocode.py
import requests
from urllib.parse import urlencode

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "SaborExpress/1.0", "Accept-Language": "pt-BR"}

def geocode_address(address, limit=1):
    """
    Consulta Nominatim e retorna o primeiro candidato: {lat, lon, display_name}
    """
    params = {"q": address, "format": "jsonv2", "limit": limit, "addressdetails": 0}
    url = f"{NOMINATIM_URL}?{urlencode(params)}"
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    data = r.json()
    if not data:
        return {"error": "Endereço não encontrado"}
    first = data[0]
    return {"lat": float(first["lat"]), "lon": float(first["lon"]), "display_name": first.get("display_name")}
