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

#list single user
class SingleUser(generics.RetrieveAPIView):
      queryset = User.objects.select_related('profile')
      serializer_class = UserSerializer

      def retrieve(self, request, *args, **kwargs):
          instance = self.get_object()
          serializer = self.get_serializer(instance)
          return Response(serializer.data, status=status.HTTP_200_OK)

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
class EditProfile(generics.UpdateAPIView):
     queryset = Profile.objects.all()
     serializer_class = ProfileSerializer
     parser_classes = [MultiPartParser, FormParser] 

     def update(self, request, *args, **kwargs):
         instance = self.get_object()
         serializer = self.serializer_class(instance, data=request.data)
         serializer.is_valid(raise_exception=True)
         serializer.save()
         return Response(serializer.data, status=status.HTTP_201_CREATED)
     
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
     
     
          