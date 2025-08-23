import osmnx as ox


def geocode_address(address: str):
    try:
        location = ox.geocode(address)
        return location[0], location[1], address
    except Exception:
        return None, None, "Não encontrado"
