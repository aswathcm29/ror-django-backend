from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

def get_location_name(latitude, longitude):
    geolocator = Nominatim(user_agent="my_geocoder")
    try:
        location = geolocator.reverse((latitude, longitude), language='en')
        if location:
            return location.address
        return 'No results found'
    except GeocoderTimedOut:
        return 'Geocoder service timed out'