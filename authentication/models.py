from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    STUDENT = 'student'
    RECRUITER = 'recruiter'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (RECRUITER, 'Recruiter'),
        (ADMIN, 'Admin'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.username}-{self.role}"
    
    def is_student(self):
        return self.role == self.STUDENT
    
    def is_recruiter(self):
        return self.role == self.RECRUITER
    
class Student(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE,primary_key=True)
    cv = models.FileField(upload_to='cv_files/', blank=True, null=True)
    cv_approved_status = models.BooleanField(default=False)
    job_status = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
    def has_cv(self):
        return bool(self.cv)

class Recruiter(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE,primary_key=True)
    company_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.username}-{self.company_name}"
