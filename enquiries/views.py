"""
Public API views — accessible without authentication.
  POST /api/contact/  →  Submit a contact form enquiry
"""
import logging
from typing import Optional

from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from .models import Enquiry
from .serializers import EnquiryCreateSerializer
from .email_utils import send_notification_email, send_confirmation_email

logger = logging.getLogger(__name__)


class ContactFormThrottle(AnonRateThrottle):
    """Limit contact form submissions to 5 per minute per IP."""
    rate = '5/minute'


@api_view(['POST'])
@throttle_classes([ContactFormThrottle])
def contact_form_submit(request):
    """
    Submit a contact form.
    Saves to MongoDB and attempts to send emails.
    Email failures are logged but NEVER cause the request to fail —
    the form submission always succeeds if the data is valid.
    """
    serializer = EnquiryCreateSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {'success': False, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    validated = serializer.validated_data
    ip = _get_client_ip(request)

    # ── Save to MongoDB ──────────────────────────────────────────────────────
    try:
        enquiry = Enquiry(
            name=validated['name'],
            email=validated['email'],
            message=validated['message'],
            ip_address=ip,
            status='new',
        )
        enquiry.save()
        logger.info(f"Enquiry saved: id={enquiry.id} email={enquiry.email}")
    except Exception as db_err:
        logger.error(f"Failed to save enquiry to MongoDB: {db_err}")
        return Response(
            {'success': False, 'message': 'Database error. Please try again later.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # ── Send emails (completely non-blocking — NEVER fails the request) ──────
    notification_ok = False
    confirmation_ok = False

    try:
        notification_ok = send_notification_email(enquiry)
    except Exception as e:
        logger.warning(f"Admin notification email failed (non-fatal): {e}")

    try:
        confirmation_ok = send_confirmation_email(enquiry)
    except Exception as e:
        logger.warning(f"Confirmation email failed (non-fatal): {e}")

    # Update email flags if at least one succeeded
    if notification_ok or confirmation_ok:
        try:
            enquiry.notification_sent = notification_ok
            enquiry.confirmation_sent = confirmation_ok
            enquiry.save()
        except Exception:
            pass  # Non-critical flag update — don't fail the request

    logger.info(
        f"Contact form submitted: enquiry={enquiry.id} | "
        f"notification_email={'✓' if notification_ok else '✗ (check SMTP config)'} | "
        f"confirmation_email={'✓' if confirmation_ok else '✗ (check SMTP config)'}"
    )

    return Response(
        {
            'success': True,
            'message': "Thank you! We'll be in touch within 1 business day.",
            'id': str(enquiry.id),
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint.
    GET /api/health/  →  { "status": "ok" }
    """
    return Response({'status': 'ok', 'service': 'ExpertiseCo CRM API'})


def _get_client_ip(request) -> Optional[str]:
    """Extract real client IP, accounting for reverse proxies."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')