from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import *
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from .serializers import *

# Create your views here.

# sign in user
class Loginview(TokenObtainPairView):
    serializer_class = obtainSerializer

# register users
class RegisterView(generics.CreateAPIView):
     queryset = User.objects.all()
     serializer_class = RegisterSerializer

# user views

#list all users
class AllUsers(generics.ListAPIView):
     queryset = User.objects.all()
     serializer_class = UserSerializer
#Update user 
class UpdateUser(generics.UpdateAPIView):
    queryset = User.objects.select_related('profile')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

#delete user account
class DeleteUser(generics.RetrieveDestroyAPIView):
     queryset = User.objects.all()
     serializer_class = UserSerializer

     def delete(self, request, *args, **kwargs):
          instance = self.get_object()
          instance.delete()
          return Response({"msg": "user Deleted successfully"})

#deactivate user 
class DeactivateUser(APIView):
     queryset = User.objects.all()
     serializer_class = UserSerializer
     
     def patch(self, request, *args, **kwargs):
          user_id = kwargs.get('pk')
          status = request.data.get('is_active')

          try:
               with transaction.atomic():
                    user = User.objects.get(pk=user_id)
                    user.is_active = status
                    user.save()

                    serializer = self.serializer_class(user)
                    return Response(serializer.data)
          except Appointment.DoesNotExist:
                    return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

#list single user
class SingleUser(generics.RetrieveAPIView):
      queryset = User.objects.select_related('profile')
      serializer_class = UserSerializer

      def retrieve(self, request, *args, **kwargs):
          instance = self.get_object()
          serializer = self.get_serializer(instance)
          return Response(serializer.data, status=status.HTTP_200_OK)
      
#list patients
class ListPatients(generics.ListAPIView):
     queryset = User.objects.select_related('profile').filter(is_patient=True)
     serializer_class = UserProfileSerializer

# Profile view

#user profile
@api_view(['GET'])
def Single_Profile(request, user_id):
     try:
          user = User.objects.select_related('profile').get(id=user_id)
     except User.DoesNotExist:
          return Response(status=status.HTTP_404_NOT_FOUND)
     if request.method == 'GET':
          serializer = UserProfileSerializer(user)
          return Response(serializer.data, status=status.HTTP_200_OK)
     
#edit profile
class EditUserProfile(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    parser_classes = [MultiPartParser, FormParser] 
    lookup_field = 'user_id'  

    def update(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')  # Extract user_id from the URL
        try:
            # Get the Profile instance for the specific user_id
            instance = self.get_object()
        except Profile.DoesNotExist:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Update the instance with the provided data
        serializer = self.serializer_class(instance, data=request.data, partial=True)  
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
     
#Appointmet View

#list Doctors
class ListDoctors(generics.ListAPIView):
     queryset = User.objects.select_related('profile').filter(is_doctor=True)
     serializer_class = UserProfileSerializer

#post appointments
class PostAppointments(generics.CreateAPIView):
     queryset = Appointment.objects.all()
     serializer_class = AppointmentSerializer

#edit appointments
class EditAppointments(generics.UpdateAPIView):
     queryset = Appointment.objects.all()
     serializer_class = AppointmentSerializer

     def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

#list doctor appointments
@api_view(['GET'])
def DoctorAppointments(request, doctor_id):
     try:
          user = User.objects.prefetch_related('appointments').get(id=doctor_id)
     except User.DoesNotExist:
          return Response(status=status.HTTP_404_NOT_FOUND)
     if request.method == 'GET':
          serializer = DoctorAppointmentSerializer(user)
          return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def PatientAppointments(request, patient_id):
     try:
          appointment = Appointment.objects.filter(user=patient_id)
     except Appointment.DoesNotExist:
          return Response(status=status.HTTP_404_NOT_FOUND)
     if request.method == 'GET':
          serializer = PatientAppointmentSerializer(appointment, many=True)
          return Response(serializer.data, status=status.HTTP_200_OK)
     
#change appointment status
class ChangeAppointmentStatus(APIView):
     queryset = Appointment.objects.all()
     serializer_class = AppointmentSerializer

     def patch(self, request, *args, **kwargs):
          appointment_id = kwargs.get('pk')
          status = request.data.get('status')

          try:
               with transaction.atomic():
                    appointment = Appointment.objects.get(pk=appointment_id)
                    appointment.status = status
                    appointment.save()

                    serializer = self.serializer_class(appointment)
                    return Response(serializer.data)
          except Appointment.DoesNotExist:
                    return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
          
#delete Appointments
class RemoveAppointments(generics.RetrieveDestroyAPIView):
     queryset = Appointment.objects.all()
     serializer_class = AppointmentSerializer

     def delete(self, request, *args, **kwargs):
          instance = self.get_object()
          instance.delete()
          return Response({"msg": "Appointment Deleted successfully"})
     

#Medical Records
class ListMedicalRecords(generics.ListAPIView):
     queryset = MedicalRecord.objects.all()
     serializer_class = MedicalRecordSerializer

# post medical records
class PostMedicalRecords(generics.CreateAPIView):
     queryset = MedicalRecord.objects.all()
     serializer_class = MedicalRecordSerializer

#patient records
@api_view(['GET'])
def PatientRecordView(request, patient_id):
     try:
          user = User.objects.prefetch_related("medical_records").get(id=patient_id)
     except User.DoesNotExist:
          return Response({"user": "user not found"})
     if request.method == 'GET':
          serializer = PatientMedicalRecordSerializer(user)
          return Response(serializer.data, status=status.HTTP_200_OK)
     
#patient delete medical records
class RemoveRecords(generics.RetrieveDestroyAPIView):
     queryset = MedicalRecord.objects.all()
     serializer_class = MedicalRecordSerializer

     def delete(self, request, *args, **kwargs):
          instance = self.get_object()
          instance.delete()
          return Response({"msg": "Medical Record Deleted successfully"})
     
#edit records
class EditRecords(generics.UpdateAPIView):
     queryset = MedicalRecord.objects.all()
     serializer_class = MedicalRecordSerializer

     def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
     
# prescriptions
class PostPrescriptions(generics.CreateAPIView):
     queryset = Prescription.objects.all()
     serializer_class = PrescriptionSerializer

#list patient prescriptions
@api_view(['GET'])
def PatientPrescriptions(request, patient_id):
     try:
          user = User.objects.prefetch_related('prescriptions').get(id=patient_id)
     except User.DoesNotExist:
          return Response({"user": "user doesnot exist"})
     if request.method == 'GET':
          serializer = PrescriptionSerializer(user, many=True)
          return Response(serializer.data, status=status.HTTP_200_OK)
     

#Reports
@api_view(['GET'])
def Daily_Appointment_trend(request, doctor_id):
    """
    Get daily appointment trends for a specific doctor, starting from their date_joined.
    Grouped by month and then by day.
    """
    try:
        doctor = User.objects.get(id=doctor_id, is_doctor=True)
    except User.DoesNotExist:
        return Response({"error": "Doctor not found"}, status=404)

    # Get the doctor's date_joined
    date_joined = doctor.date_joined.date()

    # Get today's date
    today = timezone.now().date()

    # Initialize the response structure
    trends = []

    # Loop through each month from date_joined to today
    current_date = date_joined
    while current_date <= today:
        # Get the start and end of the current month
        start_of_month = current_date.replace(day=1)
        end_of_month = (start_of_month.replace(month=start_of_month.month + 1) - timezone.timedelta(days=1))

        # Query appointments for the current month
        appointments = Appointment.objects.filter(
            doctor=doctor,
            date__range=[start_of_month, end_of_month]
        ).values('date').annotate(total_appointments=Count('id')).order_by('date')

        # Format the daily trends for the current month
        daily_trends = [
            {
                "date": appointment['date'].strftime('%Y-%m-%d'),
                "total_appointments": appointment['total_appointments']
            }
            for appointment in appointments
        ]

        # Add the month and its daily trends to the response
        trends.append({
            "month": start_of_month.strftime('%B %Y'),
            "daily_trends": daily_trends
        })

        # Move to the next month
        current_date = end_of_month + timezone.timedelta(days=1)

    return Response({
        "doctor_id": doctor_id,
        "date_joined": date_joined.strftime('%Y-%m-%d'),
        "trends": trends
    })


@api_view(['GET'])
def Daily_Reports(request, doctor_id):
    """
    Get daily reports for a specific doctor.
    """
    try:
        doctor = User.objects.get(id=doctor_id, is_doctor=True)
    except User.DoesNotExist:
        return Response({"error": "Doctor not found"}, status=404)

    # Get today's date
    today = timezone.now().date()

    # Query appointments for today
    appointments = Appointment.objects.filter(doctor=doctor, date=today)

    # Calculate totals
    total_appointments = appointments.count()
    total_patients = appointments.values('user').distinct().count()

    # Count appointments by status
    status_counts = appointments.values('status').annotate(count=Count('id'))

    # Format the response
    report = {
        "doctor_id": doctor_id,
        "date": today.strftime('%Y-%m-%d'),
        "total_appointments": total_appointments,
        "total_patients": total_patients,
        "appointments_by_status": {item['status']: item['count'] for item in status_counts}
    }

    return Response(report)
          