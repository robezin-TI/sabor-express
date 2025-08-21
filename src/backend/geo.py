from geopy.geocoders import Nominatim

_geocoder = Nominatim(user_agent="sabor_express_app")

def geocode_address(address: str):
    try:
        loc = _geocoder.geocode(address, timeout=10)
        if not loc:
            return None
        return (loc.latitude, loc.longitude)
    except Exception:
        return None
