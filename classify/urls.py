# voice_processor/urls.py
from django.urls import path
from .views import ProcessVoiceInput

urlpatterns = [
    path('v1/process-voice/', ProcessVoiceInput.as_view(), name='process_voice'),
]
