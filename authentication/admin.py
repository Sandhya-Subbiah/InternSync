from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser,Student,Recruiter

admin.site.register(CustomUser)
admin.site.register(Student)
admin.site.register(Recruiter)