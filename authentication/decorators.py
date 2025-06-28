# decorators.py
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

User = get_user_model()

def student_required(function):
    def check_user(user):
        return user.is_authenticated and user.role == User.STUDENT
    
    return user_passes_test(check_user, login_url='login')(function)

def recruiter_required(function):
    def check_user(user):
        return user.is_authenticated and user.role == User.RECRUITER
    
    return user_passes_test(check_user, login_url='login')(function)