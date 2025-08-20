from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="route-optimizer")

def geocode_address(address):
    location = geolocator.geocode(address)
    if location:
        return [location.latitude, location.longitude]
    return None
