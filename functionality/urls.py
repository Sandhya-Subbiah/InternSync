# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('upload_cv/',views.upload_cv,name='upload_cv'),
    path('create_job/',views.create_job,name='create_job'),
    path('search_job/',views.search_job,name='search_job'),
    path('apply_job/<int:job_id>',views.apply_job,name='apply_job'),
    path('applications/update-status/<int:application_id>/<str:new_status>/', views.update_application_status, name='update_application_status'),
    path('applications/all/', views.all_applications, name='all_applications'),
    path('applications/update-status/<int:application_id>/<str:new_status>/', views.update_application_status, name='update_application_status'),
    path('applications/cv/<int:application_id>/', views.download_cv, name='download_cv'),
    
]