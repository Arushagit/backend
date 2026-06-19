"""
URL routing for the enquiries app.

Public:
  POST /api/contact/        → Submit contact form
  GET  /api/health/         → Health check

Admin (JWT required):
  POST  /api/admin/login/              → Get JWT tokens
  POST  /api/admin/token/refresh/      → Refresh access token
  GET   /api/admin/stats/              → Dashboard statistics
  GET   /api/admin/enquiries/          → List all enquiries
  GET   /api/admin/enquiries/<id>/     → Get single enquiry
  PATCH /api/admin/enquiries/<id>/     → Update status
  DELETE/api/admin/enquiries/<id>/     → Delete enquiry
"""
from django.urls import path
from .views import contact_form_submit, health_check
from .admin_views import (
    admin_login,
    AdminTokenRefreshView,
    enquiry_list,
    enquiry_detail,
    dashboard_stats,
)

urlpatterns = [
    # ── Public Endpoints ──────────────────────────────────────────────────────
    path('contact/', contact_form_submit, name='contact-form-submit'),
    path('health/', health_check, name='health-check'),

    # ── Admin Auth ────────────────────────────────────────────────────────────
    path('admin/login/', admin_login, name='admin-login'),
    path('admin/token/refresh/', AdminTokenRefreshView.as_view(), name='admin-token-refresh'),

    # ── Admin Enquiry Management ──────────────────────────────────────────────
    path('admin/stats/', dashboard_stats, name='admin-stats'),
    path('admin/enquiries/', enquiry_list, name='admin-enquiry-list'),
    path('admin/enquiries/<str:pk>/', enquiry_detail, name='admin-enquiry-detail'),
]