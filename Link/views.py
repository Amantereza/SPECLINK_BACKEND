from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import *
from django.db import transaction
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
     
     
          