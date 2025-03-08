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
from django.db.models.functions import ExtractMonth, ExtractYear
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

#monthly stats
@api_view(['GET'])

def get_monthly_stats(self, doctor_id):
    try:
        # Fetch the doctor's join date
        doctor = User.objects.get(id=doctor_id)
        join_date = doctor.date_joined
        join_year = join_date.year
        join_month = join_date.month

        current_year = timezone.now().year
        current_month = timezone.now().month

        # Fetch appointments for the given doctor and annotate with year and month
        appointments = Appointment.objects.filter(doctor__id=doctor_id).annotate(
            month=ExtractMonth('created_at'),
            year=ExtractYear('created_at')
        ).filter(
            Q(year=current_year, month__lte=current_month) | Q(year=current_year - 1)
        )

        # Initialize a dictionary to store monthly stats
        monthly_data = {}
        for appointment in appointments:
            year = appointment.year
            month = appointment.month
            key = f"{year}-{month}"

            if key not in monthly_data:
                monthly_data[key] = {
                    "year": year,
                    "month": month,
                    "total_appointments": 0,
                    "total_patients": set(),  # Use a set to track unique patients
                }

            # Increment total appointments and add patient to the set
            monthly_data[key]["total_appointments"] += 1
            monthly_data[key]["total_patients"].add(appointment.user.id)

        # Convert the set of patients to a count
        for key in monthly_data:
            monthly_data[key]["total_patients"] = len(monthly_data[key]["total_patients"])

        # List of month names
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

        # Prepare the final data
        data = []
        # Add data from the join month to the current month
        for year in range(join_year, current_year + 1):
            start_month = join_month if year == join_year else 1
            end_month = current_month if year == current_year else 12

            for month in range(start_month, end_month + 1):
                key = f"{year}-{month}"
                month_name = f"{month_names[month - 1]} {year}"  # Format: "March 2025"
                if key in monthly_data:
                    data.append({
                        "month": month_name,  # Use month name instead of number
                        "total_appointments": monthly_data[key]["total_appointments"],
                        "total_patients": monthly_data[key]["total_patients"],
                    })
                else:
                    data.append({
                        "month": month_name,  # Use month name instead of number
                        "total_appointments": 0,
                        "total_patients": 0,
                    })

        # Sort the data by year and month
        data.sort(key=lambda x: (x['month']))
        return Response(data)

    except Exception as e:
        return {"error": str(e)}
     
#appointment trend            
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


# daily reports
@api_view(['GET'])
def Daily_Reports(request, doctor_id):
    """
    Get daily reports for a specific doctor for the last 7 days.
    """
    # Check if doctor exists
    try:
        doctor = User.objects.get(id=doctor_id, is_doctor=True)
    except User.DoesNotExist:
        return Response({"error": "Doctor not found"}, status=404)

    # Define date range (last 7 days, including today)
    end_date = timezone.now().date()
    start_date = end_date - timezone.timedelta(days=6)  # 7 days total

    # Query appointments for the date range in one go
    appointments = Appointment.objects.filter(
        doctor=doctor,
        date__range=[start_date, end_date]
    ).values('date', 'status', 'user').annotate(count=Count('id'))

    # Initialize daily reports dictionary
    daily_reports = {}
    for single_date in (start_date + timezone.timedelta(days=n) for n in range(7)):
        date_str = single_date.strftime('%Y-%m-%d')
        daily_reports[date_str] = {
            "doctor_id": doctor_id,
            "date": date_str,
            "total_appointments": 0,
            "total_patients": 0,
            "appointments_by_status": {
                "Cancelled": 0,
                "Approved": 0,
                "Pending": 0,
            }
        }

    # Aggregate data from appointments
    for appt in appointments:
        date_str = appt['date'].strftime('%Y-%m-%d')
        report = daily_reports[date_str]
        report["total_appointments"] += appt['count']
        if appt['status'] in report["appointments_by_status"]:
            report["appointments_by_status"][appt['status']] = appt['count']

    # Calculate distinct patients per day
    for single_date in daily_reports:
        daily_reports[single_date]["total_patients"] = (
            Appointment.objects.filter(doctor=doctor, date=single_date)
            .values('user')
            .distinct()
            .count()
        )

    # Convert to list for response
    daily_reports_list = list(daily_reports.values())

    return Response(daily_reports_list, status=200)