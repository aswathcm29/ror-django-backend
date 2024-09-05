# voice_processor/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import status
from .utils import process_audio, generate_text_response
import logging
import os
logger = logging.getLogger(__name__)

class ProcessVoiceInput(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request, format=None):
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
                logger.error(f"Error processing audio: {result['category']}")
                return Response({'error': result['text']}, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"Recognized text: {result['category']}")
            
            return Response({
                'category': result['category'],
                'text': result['text'],
                'lang': result['lang'],
            }, status=status.HTTP_200_OK)
        
        elif 'application/json' in request.content_type:
            # Handle JSON data if needed in the future
            return Response({'error': 'JSON data is not supported for this endpoint'}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
        else:
            logger.error(f"Unsupported media type: {request.content_type}")
            return Response(
                {'error': f'Unsupported media type: {request.content_type}. Use multipart/form-data with an "audio" file.'},
                status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
            )

# The rest of the files (utils.py, urls.py) remain the same as in the previous artifact


class TextVoiceGenerator(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    def post(self, request, format=None):
        text = request.data.get('text')
        lang = request.data.get('lang')

        if not text:
            return Response({'error': 'No text provided'}, status=status.HTTP_400_BAD_REQUEST)
        if not lang:
            return Response({'error': 'No language provided'}, status=status.HTTP_400_BAD_REQUEST)
        # Generate voice from text
        try:
            text_response = generate_text_response(text, lang)
            if(text_response.startswith("Error")):
                return Response({'error': text_response}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'response': text_response}, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'Error generating text and voice response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
