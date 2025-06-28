from django import forms
from django.utils import timezone
from authentication.models import CustomUser,Student,Recruiter
from .models import Job, Application

class CVUploadForm(forms.ModelForm):
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
            if not cv.name.endswith(('.pdf', '.doc', '.docx')):
                raise forms.ValidationError("Only PDF and Word documents are allowed.")
            
            # Check file size (limit to 5MB)
            if cv.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File size should not exceed 5MB.")
        else:
            raise forms.ValidationError("Please upload your CV.")
        return cv
    
class JobCreationForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'position', 'location', 'description', 'criteria', 
                  'selection_type', 'last_date_to_apply', 'salary_range', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'criteria': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'selection_type': forms.Select(attrs={'class': 'form-select'}),
            'last_date_to_apply': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'min': timezone.now().strftime('%Y-%m-%dT%H:%M')
            }, format='%Y-%m-%dT%H:%M'),
            'salary_range': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
        }

    def __init__(self, *args, **kwargs):
        super(JobCreationForm, self).__init__(*args, **kwargs)
        if self.instance.pk and self.instance.last_date_to_apply:
            self.initial['last_date_to_apply'] = self.instance.last_date_to_apply.strftime('%Y-%m-%dT%H:%M')

        # 💡 Explicitly set input_formats here
        self.fields['last_date_to_apply'].input_formats = ['%Y-%m-%dT%H:%M']

    def clean_last_date_to_apply(self):
        last_date = self.cleaned_data.get('last_date_to_apply')
        if last_date and last_date < timezone.now():
            raise forms.ValidationError("Last date to apply cannot be in the past.")
        return last_date

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['preference_order']
        widgets = {
            'preference_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10'
            }),
        }