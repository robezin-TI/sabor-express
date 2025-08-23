import osmnx as ox

def geocode_address(address: str):
    """
    Retorna (lat, lon, label) ou (None, None, 'Não encontrado')
    """
    try:
        lat, lon = ox.geocode(address)
        return float(lat), float(lon), address
    except Exception:
        return None, None, "Não encontrado"
