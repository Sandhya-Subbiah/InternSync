from django.db import models
from django.utils import timezone
from authentication.models import Student,Recruiter

class Job(models.Model):
    NORMAL = 'normal'
    FAST_TRACK = 'fast_track'
    SELECTION_TYPES = [
        (NORMAL, 'Normal Selection Process'),
        (FAST_TRACK, 'Fast Track Selection'),
    ]
    
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    criteria = models.TextField(help_text="Eligibility criteria for the job")
    selection_type = models.CharField(max_length=20, choices=SELECTION_TYPES, default=NORMAL)
    posted_date = models.DateTimeField(default=timezone.now)
    last_date_to_apply = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    position = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    salary_range = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.title} at {self.recruiter.company_name}"
    
class Application(models.Model):
    PENDING = 'pending'
    UNDER_REVIEW = 'under_review'
    SHORTLISTED_OA = 'shortlisted_oa'
    COMPLETED_OA = 'completed_oa'
    SHORTLISTED_INTERVIEW = 'shortlisted_interview'
    SELECTED = 'selected'
    REJECTED = 'rejected'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (UNDER_REVIEW, 'Under Review'),
        (SHORTLISTED_OA, 'Shortlisted for Online Assessment'),
        (COMPLETED_OA, 'Completed Online Assessment'),
        (SHORTLISTED_INTERVIEW, 'Shortlisted for Interview'),
        (SELECTED, 'Selected'),
        (REJECTED, 'Rejected'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=PENDING)
    preference_order = models.PositiveIntegerField(default=1)
    applied_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'job')
    
    def __str__(self):
        return f"{self.student.user.username} - {self.job.title}"