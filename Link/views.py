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
from datetime import timedelta, datetime
from collections import defaultdict
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

#list doctor profiles
@api_view(['GET'])
def ListDoctorProfiles(self):
    try:
          user = User.objects.select_related('profile').filter(is_doctor=True)
     except User.DoesNotExist:
          return Response(status=status.HTTP_404_NOT_FOUND)
     if request.method == 'GET':
          serializer = UserProfileSerializer(user, many=True)
          return Response(serializer.data, status=status.HTTP_200_OK)
     
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
   
    try:
        # Fetch the doctor
        doctor = User.objects.get(id=doctor_id, is_doctor=True)
    except User.DoesNotExist:
        return Response({"error": "Doctor not found"}, status=404)

    # Get the doctor's date_joined
    user_joined_date = doctor.date_joined.date()

    # Get today's date
    today = timezone.now().date()

    # Fetch appointments for the doctor from the date they joined until today
    appointments = Appointment.objects.filter(
        doctor=doctor,
        created_at__date__range=[user_joined_date, today]  # Use `date__range` for date filtering
    )

    # Aggregate appointments by day
    daily_trends = defaultdict(int)
    for appointment in appointments:
        appointment_date = appointment.created_at.date()  # Extract the date part
        daily_trends[appointment_date] += 1

    # Generate a list of all dates from the user's join date to today
    all_dates = []
    current_date = user_joined_date
    while current_date <= today:
        all_dates.append(current_date)
        current_date += timedelta(days=1)

    # Build the daily trends data, ensuring every day is included
    trends_data = []
    for date in all_dates:
        trends_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "count": daily_trends.get(date, 0)  # Default to 0 if no appointments on that day
        })

    # Group daily trends by month
    monthly_trends = defaultdict(list)
    for trend in trends_data:
        month_key = datetime.strptime(trend["date"], "%Y-%m-%d").strftime("%B %Y")  # e.g., "March 2025"
        monthly_trends[month_key].append(trend)

    # Convert the monthly trends to a list of {month: month, daily_trends: daily_trends} objects
    monthly_trends_data = [
        {"month": month, "daily_trends": daily_trends}
        for month, daily_trends in sorted(monthly_trends.items())
    ]

    return Response({
        "doctor_id": doctor_id,
        "date_joined": user_joined_date.strftime("%Y-%m-%d"),
        "monthly_trends": monthly_trends_data
    })


# daily reports
@api_view(['GET'])
def Daily_Reports(request, doctor_id):
   
    try:
        # Fetch the doctor
        doctor = User.objects.get(id=doctor_id, is_doctor=True)
    except User.DoesNotExist:
        return Response({"error": "Doctor not found"}, status=404)

    # Get the doctor's date_joined
    date_joined = doctor.date_joined.date()

    # Get today's date
    today = timezone.now().date()

    # Initialize the response structure
    daily_reports = []

    # Loop through each day from date_joined to today
    current_date = date_joined
    while current_date <= today:
        # Query appointments for the current day, grouped by status
        appointments = Appointment.objects.filter(
            doctor=doctor,
            created_at__date=current_date  # Use `created_at__date` for grouping
        ).values('status').annotate(
            total_appointments=Count('id'),
            total_patients=Count('user', distinct=True)
        )

        # Initialize the daily report
        report = {
            "doctor_id": doctor_id,
            "date": current_date.strftime('%Y-%m-%d'),  # Date in YYYY-MM-DD format
            "current_month": current_date.strftime('%B %Y'),  # Current month in "Month YYYY" format
            "total_appointments": 0,
            "total_patients": 0,
            "appointments_by_status": {
                "Cancelled": 0,
                "Approved": 0,
                "Pending": 0,
            }
        }

        # Update the report with data from appointments
        for appt in appointments:
            report["total_appointments"] += appt['total_appointments']
            report["total_patients"] = appt['total_patients']
            if appt['status'] in report["appointments_by_status"]:
                report["appointments_by_status"][appt['status']] += appt['total_appointments']

        # Append the report to the list
        daily_reports.append(report)

        # Move to the next day
        current_date += timedelta(days=1)

    return Response(daily_reports, status=200)
