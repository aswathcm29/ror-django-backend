# voice_processor/urls.py
from django.urls import path
from .views import ProcessVoiceInput, TextVoiceGenerator

urlpatterns = [
    path('v1/process-voice/', ProcessVoiceInput.as_view(), name='process_voice'),
    path('v1/text-voice-generator/', TextVoiceGenerator.as_view(), name='text_voice_generator'),
]


