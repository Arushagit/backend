"""
URL configuration for crm_backend project.
"""
from django.urls import path, include

urlpatterns = [
    path('https://backend-2v3h.onrender.com', include('enquiries.urls')),
]
