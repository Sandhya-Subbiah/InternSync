from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .forms import SignUpForm,CustomUserForm,StudentProfileForm,RecruiterProfileForm
from .models import CustomUser, Student, Recruiter
from .decorators import student_required, recruiter_required
from functionality.models import Application,Job
from django.utils import timezone


def landing(request):
    return render(request, 'landing.html')

@transaction.atomic
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Save user instance without committing
            user.set_password(form.cleaned_data['password'])  # Hash password
            user.save()  # Now save to DB

            # Create a Student or Recruiter based on role
            if user.role == CustomUser.STUDENT:
                Student.objects.create(user=user)
            elif user.role == CustomUser.RECRUITER:
                Recruiter.objects.create(
                    user=user,
                    company_name=form.cleaned_data.get('company_name')
                )

            login(request, user)  # Authenticate user after signup
            return redirect('student_dashboard' if user.role == CustomUser.STUDENT else 'recruiter_dashboard')
        else:
            print(form.errors)  # Debugging line to print form errors

    else:
        form = SignUpForm()
    
    return render(request, 'signup.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            if user.role == CustomUser.STUDENT:
                return redirect('student_dashboard')
            elif user.role == CustomUser.RECRUITER:
                return redirect('recruiter_dashboard')
            return redirect('admin_dashboard')

    return render(request, 'login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('')

@student_required
def student_dashboard(request):
    student = request.user.student
    context = {
        'cv_approved_status': student.cv_approved_status,
        'job_status': student.job_status,
    }
    return render(request, 'student_dashboard.html', context)

@recruiter_required
def recruiter_dashboard(request):
    # Get the current recruiter
    recruiter = request.user.recruiter
    
    # Get all jobs created by this recruiter
    all_jobs = Job.objects.filter(recruiter=recruiter)
    
    # Add application count to each job
    active_jobs = all_jobs.filter(is_active=True, last_date_to_apply__gt=timezone.now())
    for job in active_jobs:
        job.applications_count = Application.objects.filter(job=job).count()
    
    # Get recent applications for the recruiter's jobs
    # Optional: Filter by status if provided in query params
    status_filter = request.GET.get('status', None)
    
    applications_query = Application.objects.filter(job__recruiter=recruiter)
    if status_filter:
        applications_query = applications_query.filter(status=status_filter)
    
    recent_applications = applications_query.order_by('-applied_date')[:10]
    
    # Calculate dashboard statistics
    stats = {
        'active_jobs_count': active_jobs.count(),
        'total_applications': Application.objects.filter(job__recruiter=recruiter).count(),
        'in_process_count': Application.objects.filter(
            job__recruiter=recruiter,
            status__in=['under_review', 'shortlisted_oa', 'completed_oa', 'shortlisted_interview']
        ).count(),
        'positions_filled': Application.objects.filter(
            job__recruiter=recruiter,
            status='selected'
        ).count(),
    }
    
    context = {
        'active_jobs': active_jobs,
        'recent_applications': recent_applications,
        'stats': stats,
    }
    
    return render(request, 'recruiter_dashboard.html', context)

@login_required
def edit_profile(request):
    user = request.user
    
    if request.method == 'POST':
        user_form = CustomUserForm(request.POST, instance=user)
        
        if user.is_student():
            profile_form = StudentProfileForm(request.POST, request.FILES, instance=user.student)
        elif user.is_recruiter():
            profile_form = RecruiterProfileForm(request.POST, instance=user.recruiter)
        else:
            # Handle admin or other roles if needed
            messages.error(request, "Profile editing not available for your role.")
            return redirect('home')
            
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            
            # If student uploads a new CV, reset the approval status
            if user.is_student() and 'cv' in request.FILES:
                user.student.cv_approved_status = False
                user.student.save()
                
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')  # Redirect to profile page
    else:
        user_form = CustomUserForm(instance=user)
        
        if user.is_student():
            profile_form = StudentProfileForm(instance=user.student)
        elif user.is_recruiter():
            profile_form = RecruiterProfileForm(instance=user.recruiter)
        else:
            # Handle admin or other roles
            messages.error(request, "Profile editing not available for your role.")
            return redirect('home')
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    
    return render(request, 'edit_profile.html', context)
