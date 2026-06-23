"""
URL configuration for crm_backend project.
"""
from django.urls import path, include

urlpatterns = [
    path('api/', include('enquiries.urls')),
]
