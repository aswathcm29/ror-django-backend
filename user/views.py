import jwt
import datetime
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from django.conf import settings
from .models import Doctor, Patient
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.exceptions import NotFound



def generate_token(user):
    payload = {
        'phonenumber': user.phonenumber,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')



@api_view(['POST'])
@permission_classes([AllowAny])
def register_patient(request):
    phonenumber = request.data.get('phonenumber')

    if Patient.objects.filter(phonenumber=phonenumber).exists():
        return Response({'error': 'Phone number already exists'}, status=400)

    patient = Patient(phonenumber=phonenumber, role='patient')
    patient.save()

    token = generate_token(patient)
    return Response({'phonenumber': patient.phonenumber, 'token': token}, status=201)



@api_view(['POST'])
@permission_classes([AllowAny])
def login_patient(request):
    phonenumber = request.data.get('phonenumber')

    try:
        patient = Patient.objects.get(phonenumber=phonenumber)
    except Patient.DoesNotExist:
        return Response({'error': 'Invalid phone number'}, status=400)

    token = generate_token(patient)
    return Response({'phonenumber': patient.phonenumber, 'token': token}, status=200)



@api_view(['POST'])
@permission_classes([AllowAny])
def register_doctor(request):
    phonenumber = request.data.get('phonenumber')

    if Doctor.objects.filter(phonenumber=phonenumber).exists():
        return Response({'error': 'Phone number already exists'}, status=400)

    doctor = Doctor(phonenumber=phonenumber, role='doctor')
    doctor.save()

    token = generate_token(doctor)
    return Response({'phonenumber': doctor.phonenumber, 'token': token}, status=201)



@api_view(['POST'])
@permission_classes([AllowAny])
def login_doctor(request):
    phonenumber = request.data.get('phonenumber')

    try:
        doctor = Doctor.objects.get(phonenumber=phonenumber)
    except Doctor.DoesNotExist:
        return Response({'error': 'Invalid phone number'}, status=400)

    token = generate_token(doctor)
    return Response({'phonenumber': doctor.phonenumber, 'token': token}, status=200)



@api_view(['PATCH'])
@permission_classes([AllowAny])

def update_profile(request):
    phone_number = request.data.get('phonenumber')

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

    user.save()

    return Response({'message': f'{role.capitalize()} profile updated successfully'}, status=200)