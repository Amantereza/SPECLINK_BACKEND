from rest_framework.fields import empty
from .models import *
from rest_framework import serializers
from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError

# create your serializers
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","username", "email", "first_name", "last_name", "date_joined", "is_doctor", "is_patient", "is_staff"]

class obtainSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['is_staff'] = user.is_staff
        token['is_patient'] = user.is_patient
        token['is_doctor'] = user.is_doctor
        token['username'] = user.username
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['email'] = user.email 

        return token

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    confirm_password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ['id', 'email', 'last_name', 'first_name', 'password', 'confirm_password', 'is_staff', 'is_doctor', 'is_patient']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data

    def create(self, validated_data):
        try:
            user = User.objects.create(
                username=validated_data['email'],
                email=validated_data['email'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                is_staff=validated_data.get('is_staff', False),
                is_doctor=validated_data.get('is_doctor', False),
                is_patient=validated_data.get('is_patient', False)
            )
            user.set_password(validated_data['password'])
            user.save()
            return user
        except IntegrityError:
            raise serializers.ValidationError({"email": "A user with this email already exists."})
        
#Profile serializer
class ProfileSerializer(serializers.ModelSerializer):
     class Meta:
          model = Profile
          fields = ["id", "profile_picture", "address", "date_of_birth", "specialization", "license_number","years_of_experience", "is_doctor", "is_patient", "is_staff"]

class UserProfileSerializer(serializers.ModelSerializer):
     profile = ProfileSerializer(read_only=True)
     class Meta:
          model = User
          fields  = ["id", "email", "first_name","last_name", "username", "date_joined", "is_active", "profile"]

#appointment serializer
class AppointmentSerializer(serializers.ModelSerializer):
     class Meta:
          model = Appointment
          fields = '__all__'

     def to_representation(self, instance):
        response = super().to_representation(instance)
        response['user'] = UserSerializer(instance.user).data
        return response


#patient appointments
class PatientAppointmentSerializer(serializers.ModelSerializer):
     class Meta:
          model = Appointment
          fields = '__all__'

     def to_representation(self, instance):
        response = super().to_representation(instance)
        response['doctor'] = UserSerializer(instance.doctor).data
        return response
     
#doctor appointments
class DoctorAppointmentSerializer(serializers.ModelSerializer):
     appointments = AppointmentSerializer(read_only=True, many=True)
     class Meta:
          model = User
          fields = ["id", "email", "appointments"]


#medical records serializer
class MedicalRecordSerializer(serializers.ModelSerializer):
     class Meta:
          model = MedicalRecord
          fields = "__all__"

    
     def to_representation(self, instance):
        response = super().to_representation(instance)
        response['user'] = UserSerializer(instance.user).data
        return response


#patient medical records
class PatientMedicalRecordSerializer(serializers.ModelSerializer):
     medical_records = MedicalRecordSerializer(read_only=True, many=True)
     class Meta:
          model = User
          fields = ["id", "email", "medical_records"]

#prescriptions
class PrescriptionSerializer(serializers.ModelSerializer):
     class Meta:
          model = Prescription
          fields = "__all__"

#patient prescriptions
class PatientPrescriptionsSerializer(serializers.ModelSerializer):
     prescriptions = PrescriptionSerializer(read_only=True, many=True)
     class Meta:
          model = User
          fields = ["id", "email", "prescriptions"]
     

