"""
Admin API views — all endpoints require JWT authentication.
Uses MongoEngine QuerySet API for MongoDB operations.

Endpoints:
  POST   /api/admin/login/           → Login, get JWT tokens
  POST   /api/admin/token/refresh/   → Refresh access token
  GET    /api/admin/enquiries/       → List enquiries (paginated, filterable)
  GET    /api/admin/enquiries/{id}/  → Get single enquiry
  PATCH  /api/admin/enquiries/{id}/  → Update status
  DELETE /api/admin/enquiries/{id}/  → Delete enquiry
  GET    /api/admin/stats/           → Dashboard statistics
"""
import logging
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenRefreshView
import mongoengine

from .models import Enquiry
from .serializers import EnquiryUpdateSerializer, AdminLoginSerializer, enquiry_to_dict

logger = logging.getLogger(__name__)


# ─── Custom JWT Admin Permission ────────────────────────────────────────────────

class IsAdminJWT(BasePermission):
    """
    Validates that the JWT token contains is_admin=True claim.
    """
    def has_permission(self, request, view):
        token = request.auth
        if token is None:
            return False
        return token.get('is_admin', False)


# ─── Authentication ─────────────────────────────────────────────────────────────

@api_view(['POST'])
def admin_login(request):
    """
    Authenticate admin user and return JWT tokens.
    Credentials are validated against environment variables (no DB user needed).
    """
    serializer = AdminLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid request data.', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    username = serializer.validated_data['username']
    password = serializer.validated_data['password']

    if (username != settings.ADMIN_USERNAME or
            password != settings.ADMIN_PASSWORD):
        logger.warning(f"Failed admin login attempt for username='{username}'")
        return Response(
            {'error': 'Invalid credentials.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = _create_admin_token()
    logger.info(f"Admin login successful for username='{username}'")

    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'admin': {
            'username': settings.ADMIN_USERNAME,
            'email': settings.ADMIN_EMAIL,
        }
    })


def _create_admin_token() -> RefreshToken:
    """Create a JWT RefreshToken with admin claims (no DB user required)."""
    token = RefreshToken()
    token['user_id'] = 'admin'
    token['username'] = settings.ADMIN_USERNAME
    token['is_admin'] = True
    return token


class AdminTokenRefreshView(TokenRefreshView):
    """Refresh JWT access token."""
    pass


# ─── Enquiry CRUD ───────────────────────────────────────────────────────────────

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminJWT])
def enquiry_list(request):
    """
    List all enquiries with optional filtering and pagination.

    Query Params:
        status    — Filter by status: new | read | replied
        search    — Search name or email (case-insensitive regex)
        page      — Page number (default: 1)
        page_size — Items per page (default: 20, max: 100)
    """
    queryset = Enquiry.objects.order_by('-created_at')

    # Filter by status
    status_filter = request.query_params.get('status')
    if status_filter and status_filter in ['new', 'read', 'replied']:
        queryset = queryset.filter(status=status_filter)

    # Search by name or email (case-insensitive substring match)
    search = request.query_params.get('search', '').strip()
    if search:
        queryset = queryset.filter(
            mongoengine.Q(name__icontains=search) | mongoengine.Q(email__icontains=search)
        )

    # Paginate
    try:
        page_size = min(int(request.query_params.get('page_size', 20)), 100)
        page = max(int(request.query_params.get('page', 1)), 1)
    except (ValueError, TypeError):
        page_size, page = 20, 1

    total = queryset.count()
    start = (page - 1) * page_size
    enquiries_page = queryset.skip(start).limit(page_size)

    return Response({
        'count': total,
        'page': page,
        'page_size': page_size,
        'total_pages': max((total + page_size - 1) // page_size, 1),
        'results': [enquiry_to_dict(e) for e in enquiries_page],
    })


@api_view(['GET', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminJWT])
def enquiry_detail(request, pk):
    """
    GET    — Retrieve a single enquiry (auto-marks 'new' → 'read')
    PATCH  — Update status: { "status": "read" | "replied" }
    DELETE — Permanently delete enquiry
    """
    try:
        enquiry = Enquiry.objects.get(id=pk)
    except (Enquiry.DoesNotExist, mongoengine.errors.ValidationError):
        return Response(
            {'error': f'Enquiry not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        if enquiry.status == 'new':
            enquiry.status = 'read'
            enquiry.save()
        return Response(enquiry_to_dict(enquiry))

    elif request.method == 'PATCH':
        serializer = EnquiryUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': 'Invalid data.', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        enquiry.status = serializer.validated_data['status']
        enquiry.save()
        return Response({
            'success': True,
            'message': f'Status updated to "{enquiry.status}".',
            'enquiry': enquiry_to_dict(enquiry),
        })

    elif request.method == 'DELETE':
        name = enquiry.name
        enquiry.delete()
        logger.info(f"Admin deleted enquiry from {name}")
        return Response({'success': True, 'message': 'Enquiry deleted.'})


# ─── Dashboard Stats ────────────────────────────────────────────────────────────

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminJWT])
def dashboard_stats(request):
    """Return aggregate stats for the admin dashboard."""
    total = Enquiry.objects.count()
    new_count = Enquiry.objects.filter(status='new').count()
    read_count = Enquiry.objects.filter(status='read').count()
    replied_count = Enquiry.objects.filter(status='replied').count()
    recent = Enquiry.objects.order_by('-created_at').limit(5)

    return Response({
        'total': total,
        'new': new_count,
        'read': read_count,
        'replied': replied_count,
        'recent': [enquiry_to_dict(e) for e in recent],
    })