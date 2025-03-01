from django.contrib import admin
from .models import CustomUser,DoctorProfile
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(DoctorProfile)