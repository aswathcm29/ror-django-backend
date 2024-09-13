from django.urls import path
from . import views

urlpatterns = [
    path('patient/register', views.register_patient, name='register_patient'),
    path('doctor/register', views.register_doctor, name='register_doctor'),
    path('patient/login', views.login_patient, name='login_patient'),
    path('doctor/login', views.login_doctor, name='login_doctor'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('get-doctors',views.get_available_doctors,name='get_available_doctors'),
]