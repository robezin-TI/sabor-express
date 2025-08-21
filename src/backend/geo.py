from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="sabor_express")

def geocode_address(address: str):
    """Converte endereço para coordenadas (lat, lon)."""
    try:
        location = geolocator.geocode(address)
        if location:
            return (location.latitude, location.longitude)
    except Exception:
        return None
