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
            'longitude': doc.longitude
    })
    return Response(data, status=200)


@api_view(['GET'])
@permission_classes([AllowAny])
# View function to handle profile retrieval
def view_profile(request):
    phone_number = request.query_params.get('id')
    user_role = request.query_params.get('role')

    if not phone_number or not user_role:
        return JsonResponse({'error': 'Phone number and role are required'}, status=400)
    
    profile = utils.get_user_profile(phone_number, user_role)

    if profile:
        # Convert profile to dictionary and return as JSON response
        return JsonResponse({'message': 'User found', 'profile': utils.profile_to_dict(profile, user_role)}, status=200)
    else:
        return JsonResponse({'message': 'User not found'}, status=404)
    