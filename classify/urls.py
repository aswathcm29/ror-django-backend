# voice_processor/urls.py
from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path('v1/process-voice/', views.process_voice_input, name='process_voice'),
    path('v1/medical-chatbot/', views.medical_chatbot, name='medical-chatbot'),
    path('v1/check-navigation/',views.voice_navigation,name='check-navigation'),
]


