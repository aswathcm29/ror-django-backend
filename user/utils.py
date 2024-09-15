from geopy.geocoders import Nominatim
from .models import Doctor, Patient




def get_location_from_coordinates(latitude, longitude):
    geolocator = Nominatim(user_agent="geoapiExercises")
    try:
        location = geolocator.reverse(f"{latitude}, {longitude}", language='en')
        return location.address
    except Exception as e:
        return None

def modify_profile(request, phone_number, role):
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    location_name = request.data.get('location_name')
    user = get_user_profile(phone_number, role)
    fields_to_update = {
        'doctor': ['name', 'phonenumber', 'specialization', 'experience_years','bio','latitude','longitude','location_name'],
        'patient': ['name', 'phonenumber', 'medical_history', 'age', 'height', 'weight', 'gender', 'bloodgroup', 'location_name','bio','latitude','longitude']
    }

    if role not in fields_to_update:
        return 'Error invalid role'

    for field in fields_to_update[role]:
        if field in request.data and request.data.get(field) is not None:
            setattr(user, field, request.data.get(field))

    if (location_name=="") and (latitude or longitude) :
        try:
            if latitude.strip() == '':
                raise ValueError("Empty string provided for latitude")

            user.latitude = latitude
            user.longitude = longitude

            if latitude is not None and latitude is not None:
                address = get_location_from_coordinates(latitude, longitude)
                if address:
                    user.location_name = address
                else:
                    return 'Error unable to get location from coordinates'

        except ValueError:
            return 'Error invalid latitude or longitude'

    user.save()

    return 'Profile updated successfully'


def get_user_profile(phone_number, user_role):
    try:
        if user_role == 'doctor':
            profile = Doctor.objects.get(phonenumber=phone_number)
        elif user_role == 'patient':
            profile = Patient.objects.get(phonenumber=phone_number)
        else:
            return {'error': 'Invalid user role'}
        
        return profile  # Return the profile object if found
    except (Doctor.DoesNotExist, Patient.DoesNotExist):
        return None  # Return None if the user is not found

    
def profile_to_dict(profile, user_role):
    if user_role == 'doctor':
        return {
            'name': profile.name,
            'phonenumber': profile.phonenumber,
            'specialization': profile.specialization,
            'experience_years': profile.experience_years,
            'location_name': profile.location_name,
            'latitude': profile.latitude,
            'longitude': profile.longitude,
            'bio': profile.bio,
        }
    elif user_role == 'patient':
        return {
        'name': profile.name,
        'phonenumber': profile.phonenumber,
        'role': profile.role,
        'location_name': profile.location_name,
        'latitude': profile.latitude,
        'longitude': profile.longitude,
        'bio': profile.bio,
        'height': profile.height,
        'weight': profile.weight,
        'bloodgroup': profile.bloodgroup,
        'gender': profile.gender
    }
    return None
