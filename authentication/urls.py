# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',views.landing,name=''),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/recruiter/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('logout/',views.user_logout,name='logout'),
    
    path('edit_profile/',views.edit_profile,name='edit_profile')
]