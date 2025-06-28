from django.shortcuts import render,redirect,get_object_or_404
from authentication.decorators import student_required,recruiter_required
from django.contrib import messages
from django.http import HttpResponseForbidden, FileResponse
from .forms import CVUploadForm
from .models import Job, Application
from .forms import JobCreationForm, JobApplicationForm
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone

@student_required
def upload_cv(request):
    if request.method == 'POST':
        form = CVUploadForm(request.POST, request.FILES, instance=request.user.student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your CV has been uploaded successfully!')
            return redirect('student_dashboard')  # Redirect to appropriate page after successful upload
        else:
            # Form validation errors will be displayed on the page
            pass
    else:
        form = CVUploadForm(instance=request.user.student)
    
    return render(request, 'upload_cv.html', {'form': form})

@recruiter_required
def create_job(request):
    if not request.user.is_recruiter():
        messages.error(request, "Access denied. Only recruiters can post jobs.")
        return redirect('home')
    
    if request.method == 'POST':
        form = JobCreationForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user.recruiter
            job.save()
            messages.success(request, "Job posted successfully!")
            return redirect('recruiter_dashboard')  # Redirect to recruiter dashboard
    else:
        form = JobCreationForm()
    
    return render(request, 'create_job.html', {'form': form})

@student_required
def search_job(request):
    if not request.user.is_student():
        messages.error(request, "Access denied. Only students can search for jobs.")
        return redirect('home')
    
    jobs = Job.objects.filter(is_active=True, last_date_to_apply__gt=timezone.now())
    
    # Get all unique locations for the filter dropdown
    locations = Job.objects.values_list('location', flat=True).distinct()
    
    # Get all jobs the student has already applied to
    applied_job_ids = Application.objects.filter(student=request.user.student).values_list('job_id', flat=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) | 
            Q(position__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(recruiter__company_name__icontains=search_query)
        )
    
    # Filter by location
    location = request.GET.get('location', '')
    if location:
        jobs = jobs.filter(location=location)
        
    # Filter by selection type
    selection_type = request.GET.get('selection_type', '')
    if selection_type:
        jobs = jobs.filter(selection_type=selection_type)
    
    # Pagination
    paginator = Paginator(jobs, 10)  # Show 10 jobs per page
    page = request.GET.get('page')
    jobs = paginator.get_page(page)

    context = {
        'jobs': jobs,
        'locations': locations,
        'applied_job_ids': applied_job_ids,
    }
    
    return render(request, 'search_job.html', context)

@student_required
def apply_job(request, job_id):
    if not request.user.is_student():
        messages.error(request, "Access denied. Only students can apply for jobs.")
        return redirect('home')
    
    job = get_object_or_404(Job, pk=job_id, is_active=True)
    student = request.user.student
    
    # Check if student has already applied
    if Application.objects.filter(student=student, job=job).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect('search_job')
    
    # Check if application deadline has passed
    if job.last_date_to_apply < timezone.now():
        messages.error(request, "The application deadline has passed.")
        return redirect('search_job')
    
    # Check if student has CV
    has_cv = bool(student.cv)
    cv_approved = student.cv_approved_status if has_cv else False
    can_apply = has_cv  # Students can apply even if CV is not approved yet
    
    if request.method == 'POST':
        if not has_cv:
            messages.error(request, "You need to upload your CV before applying.")
            return redirect('edit_profile')
        
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.student = student
            application.job = job
            application.save()
            messages.success(request, f"Applied successfully for {job.title}!")
            return redirect('search_job')
    else:
        form = JobApplicationForm()
    
    context = {
        'job': job,
        'form': form,
        'has_cv': has_cv,
        'cv_approved': cv_approved,
        'can_apply': can_apply,
    }
    
    return render(request, 'apply_job.html', context)

@recruiter_required
def update_application_status(request, application_id, new_status):
    recruiter = request.user.recruiter
    application = get_object_or_404(Application, id=application_id, job__recruiter=recruiter)

    # Validate the status
    valid_statuses = [choice[0] for choice in Application.STATUS_CHOICES]
    if new_status not in valid_statuses:
        messages.error(request, "Invalid application status.")
    else:
        application.status = new_status
        application.save()
        status_display = dict(Application.STATUS_CHOICES)[new_status]
        messages.success(request, f"Application status updated to {status_display}.")

    # Render the all_applications.html template with fresh data
    applications = Application.objects.filter(job__recruiter=recruiter).order_by('-applied_date')
    
    # Apply the same filters as in all_applications view
    status_filter = request.GET.get('status', None)
    if status_filter:
        applications = applications.filter(status=status_filter)

    job_filter = request.GET.get('job', None)
    if job_filter:
        applications = applications.filter(job_id=job_filter)

    jobs = Job.objects.filter(recruiter=recruiter)

    context = {
        'applications': applications,
        'jobs': jobs,
    }

    return render(request, 'all_applications.html', context)


@recruiter_required
def all_applications(request):
    recruiter = request.user.recruiter

    applications = Application.objects.filter(job__recruiter=recruiter).order_by('-applied_date')

    status_filter = request.GET.get('status', None)
    if status_filter:
        applications = applications.filter(status=status_filter)

    jobs = Job.objects.filter(recruiter=recruiter)

    job_filter = request.GET.get('job', None)
    if job_filter:
        applications = applications.filter(job_id=job_filter)

    context = {
        'applications': applications,
        'jobs': jobs,
    }

    return render(request, 'all_applications.html', context)


@recruiter_required
def download_cv(request, application_id):
    recruiter = request.user.recruiter
    application = get_object_or_404(Application, id=application_id, job__recruiter=recruiter)
    
    # Check if student has a CV
    if not application.student.cv:
        messages.error(request, "This student has not uploaded a CV.")
        return redirect('view_applicants', job_id=application.job.id)
    
    # Serve the CV file
    try:
        return FileResponse(application.student.cv.open(), as_attachment=True, filename=f"{application.student.user.get_full_name()}_CV.pdf")
    except Exception as e:
        messages.error(request, f"Error downloading CV: {str(e)}")
        return redirect('view_applicants', job_id=application.job.id)
