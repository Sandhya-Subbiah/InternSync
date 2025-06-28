from django import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from .models import CustomUser,Student,Recruiter

class SignUpForm(forms.ModelForm):
    STUDENT = 'student'
    RECRUITER = 'recruiter'

    ROLE_CHOICES = [
        (STUDENT,'Student'),
        (RECRUITER,'Recruiter'),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES,widget=forms.RadioSelect(attrs={'class':'form-check-input'}))
    email = forms.EmailField(required=True,widget=forms.EmailInput(attrs={'class':'form-control','placeholder': 'Enter your email'}))
    password = forms.CharField(required=True,widget=forms.PasswordInput(attrs={'class':'form-control','placeholder': 'Enter your password'}))

    #Field for recruiter
    company_name = forms.CharField(max_length=50,required=False,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter Company Name'}))

    class Meta:
        model = CustomUser
        fields = ['username','email','password','role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'id': 'username-field', 'placeholder': 'Enter username'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        company_name = cleaned_data.get('company_name')
        
        if role == self.RECRUITER and not company_name:
            self.add_error('company_name', 'Company name is required for recruiters')
            
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Hash the password
        if commit:
            user.save()
        return user

class CustomUserForm(UserChangeForm):
    password = None  # Remove password field from form
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['cv']
        widgets = {
            'cv': forms.FileInput(attrs={'class': 'form-control'})
        }
        
    def clean_cv(self):
        cv = self.cleaned_data.get('cv')
        if cv:
            # Check file type
            if not cv.name.lower().endswith(('.pdf', '.doc', '.docx')):
                raise forms.ValidationError("Only PDF and Word documents are allowed.")
            # Check file size (limit to 5MB)
            if cv.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File size should not exceed 5MB.")
        return cv

class RecruiterProfileForm(forms.ModelForm):
    class Meta:
        model = Recruiter
        fields = ['company_name']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'})
        }