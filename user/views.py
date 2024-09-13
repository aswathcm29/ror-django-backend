import jwt
import datetime
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.conf import settings
from .models import Doctor, Patient
from . import doctor
from geopy.geocoders import Nominatim


def get_location_from_coordinates(latitude, longitude):
    geolocator = Nominatim(user_agent="geoapiExercises")
    try:
        location = geolocator.reverse(f"{latitude}, {longitude}", language='en')
        return location.address
    except Exception as e:
        return None
    
def generate_token(user):
    payload = {
        'phonenumber': user.phonenumber,
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
    return Response({'phonenumber': patient.phonenumber, 'token': token}, status=200)




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

    latitude_float = None
    longitude_float = None
    location_name = None

    try:
        if latitude:
            latitude_float = float(latitude)
        if longitude:
            longitude_float = float(longitude)
    except ValueError:
        return Response({'error': 'Latitude and Longitude must be valid numbers.'}, status=400)

    if latitude_float is not None and longitude_float is not None:
        location_name = get_location_from_coordinates(latitude_float, longitude_float)

    patient = Patient(
        phonenumber=phonenumber,
        latitude=latitude_float,
        longitude=longitude_float,
        location_name=location_name,
        role='patient'
    )
    patient.save()

    token = generate_token(patient)
    return Response({'phonenumber': patient.phonenumber, 'token': token}, status=201)

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

    latitude_float = None
    longitude_float = None
    location_name = None

    try:
        if latitude:
            latitude_float = float(latitude)
        if longitude:
            longitude_float = float(longitude)
    except ValueError:
        return Response({'error': 'Latitude and Longitude must be valid numbers.'}, status=400)

    if latitude_float is not None and longitude_float is not None:
        location_name = get_location_from_coordinates(latitude_float, longitude_float)

    doctor = Doctor(
        phonenumber=phonenumber,
        latitude=latitude_float,
        longitude=longitude_float,
        location_name=location_name,
        role='doctor'
    )
    doctor.save()

    token = generate_token(doctor)
    return Response({'phonenumber': doctor.phonenumber, 'token': token}, status=201)

@api_view(['PATCH'])
@permission_classes([AllowAny])
def update_profile(request):
    phone_number = request.data.get('phonenumber')
    latitude = request.data.get('latitude')  
    longitude = request.data.get('longitude') 
    print(type(latitude), type(longitude))
    if not phone_number:
        return Response({'error': 'Phone number is required'}, status=400)

    try:
        try:    
            user = Doctor.objects.get(phonenumber=phone_number)
        except Doctor.DoesNotExist:
            user = Patient.objects.get(phonenumber=phone_number)
    except (Doctor.DoesNotExist, Patient.DoesNotExist):
        return Response({'error': 'User not found with the provided phone number.'}, status=404)

    role = user.role

    fields_to_update = {
        'doctor': ['name', 'phonenumber', 'specialization', 'experience_years', 'location_name'],
        'patient': ['name', 'phonenumber', 'medical_history', 'age', 'height', 'weight', 'gender', 'bloodgroup', 'location_name']
    }

    if role not in fields_to_update:
        return Response({'error': 'Invalid role'}, status=400)

    for field in fields_to_update[role]:
        if field in request.data and request.data.get(field) is not None:
            setattr(user, field, request.data.get(field))

    if latitude or longitude:
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
                    return Response({'error': 'Unable to fetch location from coordinates.'}, status=400)

        except ValueError:
            return Response({'error': 'Latitude and Longitude must be valid numbers.'}, status=400)

    user.save()

    return Response({'message': f'{role.capitalize()} profile updated successfully'}, status=200)


@api_view(['GET'])
@permission_classes([AllowAny])
def find_nearby_doctors(request):
    phonenumber = request.query_params.get('phonenumber')
    
    if not phonenumber:
        return Response({'error': 'Phone number is required'}, status=400)

    try:
        patient = Patient.objects.get(phonenumber=phonenumber)
    except Patient.DoesNotExist:
        return Response({'error': 'Patient not found with the provided phone number.'}, status=404)
    
    if patient.latitude is None or patient.longitude is None:
        return Response({'error': 'Patient coordinates are not available.'}, status=404)

    patient_location = Point(patient.longitude, patient.latitude, srid=4326)
    
    nearby_doctors = Doctor.objects.filter(
        location__distance_lt=(patient_location, D(km=15))
    )
    
    doctors_list = [
        {
            'name': doctor.name,
            'phonenumber': doctor.phonenumber,
            'specialization': doctor.specialization,
            'experience_years': doctor.experience_years,
            'location_name': doctor.location_name,
            'distance': doctor.location.distance(patient_location)  # distance in meters
        }
        for doctor in nearby_doctors
    ]

    return Response({'doctors': doctors_list}, status=200)

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
            'longitude': doc.longitude
        })
    return Response(data, status=200)
