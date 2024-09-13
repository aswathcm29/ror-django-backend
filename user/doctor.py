from .models import Doctor, Patient




def doctor_data(specialization = None, location_name = None):
    doctors = Doctor.objects.all()
    print('incoming')
    if specialization:
        doctors = doctors.filter(specialization = specialization)
    if location_name:
        doctors = doctors.filter(location_name = location_name)
    return doctors


