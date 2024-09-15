import jwt
import datetime
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.http import JsonResponse    
from django.conf import settings
from .models import Doctor, Patient
from . import doctor
from . import utils
from geopy.geocoders import Nominatim
import math
from geopy.distance import geodesic



def haversine(lat1, lon1, lat2, lon2):
    R = 6371 
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
 

def get_location_from_coordinates(latitude, longitude):
    geolocator = Nominatim(user_agent="geoapiExercises")
    try:
        location = geolocator.reverse(f"{latitude}, {longitude}", language='en')
        return location.address
    except Exception as e:
        return None
    

def generate_token(user):
    payload = {
        'id': user.phonenumber,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')



@api_view(['POST'])
@permission_classes([AllowAny])
def login_patient(request):
    phonenumber = request.data.get('phonenumber')
    
    if not phonenumber:
        return Response({'error': 'Phone number is required'}, status=400)

    try:
        patient = Patient.objects.get(phonenumber=phonenumber)
    except Patient.DoesNotExist:
        return Response({'error': 'Invalid phone number'}, status=400)

    token = generate_token(patient)
    return JsonResponse({'phonenumber': patient.phonenumber, 'token': token}, status=200)



@api_view(['POST'])
@permission_classes([AllowAny])
def login_doctor(request):
    phonenumber = request.data.get('phonenumber')
    
    if not phonenumber:
        return Response({'error': 'Phone number is required'}, status=400)

    try:
        doctor = Doctor.objects.get(phonenumber=phonenumber)
    except Doctor.DoesNotExist:
        return Response({'error': 'Invalid phone number'}, status=400)

    token = generate_token(doctor)
    return Response({'phonenumber': doctor.phonenumber, 'token': token}, status=200)



@api_view(['POST'])
@permission_classes([AllowAny])
def register_patient(request):
    phonenumber = request.data.get('phonenumber')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    
    if not phonenumber:
        return Response({'error': 'Phone number is required'}, status=400)

    if Patient.objects.filter(phonenumber=phonenumber).exists():
        return Response({'error': 'Phone number already exists'}, status=400)

    location_name = None

    if latitude is not None and latitude is not None:
        address = get_location_from_coordinates(latitude, longitude)
        if address:
            location_name = address
        

    patient = Patient(
        name="Varsha",
        phonenumber=phonenumber,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        role='patient'
    )
    patient.save()

    token = generate_token(patient)
    return JsonResponse({'phonenumber': patient.phonenumber, 'token': token}, status=201)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_doctor(request):
    phonenumber = request.data.get('phonenumber')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    
    if not phonenumber:
        return Response({'error': 'Phone number is required'}, status=400)

    if Doctor.objects.filter(phonenumber=phonenumber).exists():
        return Response({'error': 'Phone number already exists'}, status=400)
    
    location_name=None
    
    if latitude is not None and latitude is not None:
        address = get_location_from_coordinates(latitude, longitude)
        if address:
            location_name = address
        
    doctor = Doctor(
        name="Dr.Strange",
        phonenumber=phonenumber,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        role='doctor'
    )
    doctor.save()

    token = generate_token(doctor)
    return JsonResponse({'phonenumber': doctor.phonenumber, 'token': token}, status=201)


@api_view(['PATCH'])
@permission_classes([AllowAny])
def update_profile(request):
    phone_number = request.query_params.get('id')
    user_role = request.query_params.get('user_role')
    if not phone_number:
        return Response({'error': 'Phone number is required'}, status=400)
    
    result = utils.modify_profile(request, phone_number, user_role)

    if 'Error' in result :
        return JsonResponse({'error':result}, status=400)
    
    return JsonResponse({'message': f'{user_role.capitalize()} profile updated successfully'}, status=200)




@api_view(['GET'])
@permission_classes([AllowAny])
def get_available_doctors(request):
    specialization = request.query_params.get('specialization', None)
    location_name = request.query_params.get('location_name', None)
    doctors = doctor.doctor_data(specialization=specialization, location_name=location_name)
    data = []
    for doc in doctors:
        data.append({
            'name': doc.name,
            'specialization': doc.specialization,
            'experience_years': doc.experience_years,
            'location_name': doc.location_name,
            'latitude': doc.latitude,
            'longitude': doc.longitude,
            'bio': doc.bio
    })
    return Response(data, status=200)


@api_view(['GET'])
@permission_classes([AllowAny])
def view_profile(request):
    phone_number = request.query_params.get('id')
    user_role = request.query_params.get('role')

    if not phone_number or not user_role:
        return JsonResponse({'error': 'Phone number and role are required'}, status=400)
    
    profile = utils.get_user_profile(phone_number, user_role)

    if profile:
        return JsonResponse({'message': 'User found', 'profile': utils.profile_to_dict(profile, user_role)}, status=200)
    else:
        return JsonResponse({'message': 'User not found'}, status=404)
    


@api_view(['GET'])
@permission_classes([AllowAny])
def find_nearest_doctors(request):
    phonenumber = request.query_params.get('phonenumber')
    role = request.query_params.get('role')

    if not phonenumber or role != 'patient':
        return JsonResponse({'error': 'Valid phone number and patient role are required'}, status=400)

    try:
        patient = Patient.objects.get(phonenumber=phonenumber)
        patient_lat = patient.latitude
        patient_lon = patient.longitude
    except Patient.DoesNotExist:
        return JsonResponse({'error': 'Patient not found'}, status=404)

    if not patient_lat or not patient_lon:
        return JsonResponse({'error': 'Patient location not available'}, status=400)

    doctors = Doctor.objects.all()

    nearby_doctors = []
    for doctor in doctors:
        if doctor.latitude is not None and doctor.longitude is not None:
            distance = haversine(patient_lat, patient_lon, doctor.latitude, doctor.longitude)
            if distance <= 10:
                nearby_doctors.append({
                    'name': doctor.name,
                    'specialization': doctor.specialization,
                    'experience_years': doctor.experience_years,
                    'location_name': doctor.location_name,
                    'latitude': doctor.latitude,
                    'longitude': doctor.longitude,
                    'distance_km': round(distance, 2) 
                })

    return JsonResponse({'nearby_doctors': nearby_doctors}, status=200)


@api_view(['GET'])
@permission_classes([AllowAny])
def nearby_hospital(request):
    phone_number = request.query_params.get('id')
    user_role = request.query_params.get('user_role')
    specialization = request.query_params.get('specialization')

    profile = utils.get_user_profile(phone_number, user_role)
    profile = utils.profile_to_dict(profile,user_role)
    print("profile",profile)
    if not profile:
        return JsonResponse({'error': 'User not found'}, status=404)
    if not profile['latitude'] or not profile['longitude']:
        return JsonResponse({'error': 'Location not available'}, status=400)
    hospitals = utils.get_nearby_medical_centers(profile['latitude'], profile['longitude'], specialization=specialization)
    calculate_hospital_distance = utils.find_hospital_distance(hospitals=hospitals,user_lat = profile['latitude'],user_long = profile['longitude'])

    return JsonResponse({'hospitals': calculate_hospital_distance}, status=200)
    
