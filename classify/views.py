# voice_processor/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import status
from .utils import process_audio
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
            text = process_audio(audio_file)
            if text.startswith("Error") or text == "Speech could not be recognized":
                logger.error(f"Error processing audio: {text}")
                return Response({'error': text}, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"Recognized text: {text}")
            
            return Response({
                'text': text
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