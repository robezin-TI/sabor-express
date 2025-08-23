import osmnx as ox

ox.settings.use_cache = True
ox.settings.log_console = False
ox.settings.timeout = 180


def geocode_address(address: str):
    """
    Retorna (lat, lon, label) ou (None, None, 'Não encontrado')
    """
    try:
        lat, lon = ox.geocoder.geocode(address)
        return float(lat), float(lon), address
    except Exception:
        return None, None, "Não encontrado"
