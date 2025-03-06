from django.contrib import admin
from .models import *

# Register your models here.
class UsersAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'first_name', 'last_name', 'date_joined']

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'date_joined']

admin.site.register(User, UsersAdmin)
admin.site.register(Profile, ProfileAdmin)