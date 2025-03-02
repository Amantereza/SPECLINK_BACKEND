from django.urls import path
from .views import *

urlpatterns = [
    # Auth views
     path('login', Loginview.as_view()),
     path('register', RegisterView.as_view()),

    #  user views
    path('update_user/<int:pk>', UpdateUser.as_view()),
    path('single_user/<int:pk>', SingleUser.as_view()),
    path('delete_user/<int:pk>', DeleteUser.as_view()),

    #  profile views
    path('user_profile/<int:user_id>', Single_Profile),
    path('EditProfile/<int:pk>', EditProfile.as_view()),

    #appointment views
    path('list_doctors', ListDoctors.as_view()),
    path('post_appointements',  PostAppointments.as_view()),
    path('doctor_appointments/<int:doctor_id>', DoctorAppointments),
    path('change_appointment_status/<int:pk>', ChangeAppointmentStatus.as_view()),
    path('delete_appointments/<int:pk>', RemoveAppointments.as_view()),

    #medical records view
    path('list_medical_records', ListMedicalRecords.as_view()),
    path('post_medical_records', PostMedicalRecords.as_view()),
    path('patient_records/<int:patient_id>', PatientRecordView),
    path('remove_records/<int:pk>', RemoveRecords.as_view()),

    #Prescriptions views
    path('patient_prescriptions/<int:patient_id>', PatientPrescriptions),
    path('write_prescriptions', PostPrescriptions.as_view()),
]
