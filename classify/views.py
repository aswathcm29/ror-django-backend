from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import status
from django.http import JsonResponse
from .utils import process_audio, generate_text_response, classify_page,classify_specialization
import logging 
import os
from user.models import Doctor

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def process_voice_input(request):
    """
    API View to process voice input and handle the file.
    """
    logger.info(f"Received request with Content-Type: {request.content_type}")

    if 'multipart/form-data' in request.content_type:
        audio_file = request.FILES.get('voice_input')
        if not audio_file:
            logger.warning("No audio file provided in the request")
            return Response({'error': 'No audio file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"Processing voice input from file: {audio_file.name}")
        
        # Process the voice input
        result = process_audio(audio_file)

        if result['text'].startswith("Error") or result['text'] == "Speech could not be recognized":
            logger.error(f"Error processing audio: {result['text']}")
            return Response({'error': result['text']}, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"Recognized text: {result['text']}")
        
        return Response({
            'category': result['category'],
            'text': result['text'],
            'lang': result['lang'],
        }, status=status.HTTP_200_OK)
    
    elif 'application/json' in request.content_type:
        return Response({'error': 'JSON data is not supported for this endpoint'}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    
    else:
        logger.error(f"Unsupported media type: {request.content_type}")
        return Response(
            {'error': f'Unsupported media type: {request.content_type}. Use multipart/form-data with an "audio" file.'},
            status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        )

# @api_view(['POST'])
# @permission_classes([AllowAny])
# def medical_chatbot(request):
#     """
#     API View to generate text and voice response from the given text.
#     """
#     text = request.data.get('text')
#     lang = request.data.get('lang')
#     id = request.query_params.get('id')

#     if not text:
#         return Response({'error': 'No text provided'}, status=status.HTTP_400_BAD_REQUEST)
#     if not lang:
#         return Response({'error': 'No language provided'}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         text_response = generate_text_response(text, lang)
#         if text_response.startswith("Error"):
#             return Response({'error': text_response}, status=status.HTTP_400_BAD_REQUEST)

#         response_data = {
#             'text_response': text_response,
#             'voice_response': "working on it",
#         }   
            
#         return JsonResponse(response_data)
#     except Exception as e:
#         logger.error("Error generating text and voice response", exc_info=True)
#         return Response({'error': 'Error generating text and voice response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def voice_navigation(request):
    input_text = request.data.get('query', '')
    lang = request.data.get('lang', 'en')  
    
    if not input_text:
        return Response({'error': 'No query provided'}, status=status.HTTP_400_BAD_REQUEST)

    logger.info(f"Received voice navigation query: {input_text}")

    category = classify_page(input_text, lang)

    if "Error" in category:
        return Response({'error': category}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    logger.info(f"Query categorized under: {category}")

    response_data = {'category': category}

    if category == 'medibot':
        try:
            detailed_response = generate_text_response(input_text, lang)
            if detailed_response.startswith("Error"):
                return Response({'error': detailed_response}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            response_data['text_response'] = detailed_response
        except Exception as e:
            logger.error("Error generating detailed response", exc_info=True)
            return Response({'error': 'Error generating detailed response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(response_data)


@api_view(['POST'])
@permission_classes([AllowAny])
def medical_chatbot(request):
    input_text = request.data.get('text')
    lang = request.data.get('lang', 'en')
    print(input_text)
    if not input_text:
        return JsonResponse({"error": "Query is required"}, status=400)

    try:
        logging.info(f"Classifying specialization for input: {input_text}")
        specialization = classify_specialization(input_text)
        print(specialization)
        logging.info(f"Classified specialization: {specialization}")

    except Exception as e:
        logging.error(f"Error classifying specialization: {str(e)}")
        return JsonResponse({"error": "Error classifying specialization"}, status=500)

    try:
        logging.info(f"Generating medical remedy for input: {input_text}")
        print(input_text)
        remedy = generate_text_response(input_text,lang)
        print(remedy)
        logging.info(f"Medical remedy generated: {remedy}")

    except Exception as e:
        logging.error(f"Error generating medical remedy: {str(e)}")
        return JsonResponse({"error": "Error generating medical remedy"}, status=500)

    try:
        logging.info(f"Fetching doctors for specialization: {specialization}")
        doctors = Doctor.objects.filter(specialization=specialization).values()
        doctor_list = list(doctors)
        logging.info(f"Found {len(doctor_list)} doctors under specialization {specialization}")

    except Exception as e:
        logging.error(f"Error fetching doctors: {str(e)}")
        return JsonResponse({"error": "Error fetching doctors"}, status=500)

    response_data = {
        "text_response": remedy,
        "specialization": specialization,
        "doctors": doctor_list,
    }
    return JsonResponse(response_data, status=200)