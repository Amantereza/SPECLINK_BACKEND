from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

# Custom User Model to handle Patients, Doctors, and Admins
class User(AbstractUser):
    is_patient = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    confirm_password = models.CharField(max_length=255)

# Profile Model (Automatically created when a user signs up)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    specialization = models.CharField(max_length=100, null=True, blank=True)
    license_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0, null=True, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_patient = models.BooleanField()
    is_doctor = models.BooleanField()
    is_staff = models.BooleanField()

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Signal to create a profile when a user is created
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, first_name=instance.first_name, last_name=instance.last_name, email=instance.email, is_patient=instance.is_patient, is_doctor=instance.is_doctor, is_staff=instance.is_staff, date_joined=instance.date_joined)

def save_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


post_save.connect(create_profile, sender=User)
post_save.connect(save_profile, sender=User) 

# Patient Model
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient')
    medical_history = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Appointment Model
class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, default='Pending')
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Medical Record Model
class MedicalRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medical_records')
    diagnosis = models.TextField()
    treatment = models.TextField()
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Prescription Model
class Prescription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prescriptions')
    medication = models.TextField()
    dosage = models.CharField(max_length=100)
    instructions = models.TextField()
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Subscription Model (Optional for Patients)
class Subscription(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='subscription')
    plan_name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Message Model (For Chat between Patients and Doctors)
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


# Report Model (For Admins)
class Report(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    total_patients = models.PositiveIntegerField(default=0)
    total_appointments = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
