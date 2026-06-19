"""
Email utilities for the ExpertiseCo CRM.

Sends two types of emails:
  1. Admin notification — when a new enquiry is submitted.
  2. User confirmation — confirms receipt to the form submitter.

Uses Django's EmailMultiAlternatives for HTML + plain-text fallback.
"""
import html
import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone

logger = logging.getLogger(__name__)


# ─── HTML Templates ────────────────────────────────────────────────────────────
#
# IMPORTANT: All user-submitted values (name, email, message) MUST be passed
# through html.escape() before being interpolated into the HTML bodies below.
# Without this, a malicious form submission containing <script> or other markup
# would be injected directly into the admin's/submitter's rendered email.

def _notification_html(enquiry) -> str:
    """HTML body for admin notification email."""
    submitted_at = timezone.localtime(enquiry.created_at).strftime('%B %d, %Y at %I:%M %p')
    safe_name = html.escape(enquiry.name)
    safe_email = html.escape(enquiry.email)
    safe_message = html.escape(enquiry.message)
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>New Enquiry — ExpertiseCo</title>
</head>
<body style="margin:0;padding:0;background:#0f172a;font-family:'Segoe UI',Roboto,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f172a;padding:40px 20px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="background:#1e293b;border-radius:16px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.4);">
          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#6366f1,#8b5cf6);padding:32px 40px;">
              <h1 style="margin:0;color:#fff;font-size:24px;font-weight:700;letter-spacing:-0.5px;">
                📬 New Enquiry Received
              </h1>
              <p style="margin:8px 0 0;color:rgba(255,255,255,0.75);font-size:14px;">
                ExpertiseCo CRM — {submitted_at}
              </p>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding:40px;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="padding-bottom:24px;">
                    <p style="margin:0 0 6px;color:#94a3b8;font-size:12px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">From</p>
                    <p style="margin:0;color:#f1f5f9;font-size:18px;font-weight:600;">{safe_name}</p>
                  </td>
                </tr>
                <tr>
                  <td style="padding-bottom:24px;">
                    <p style="margin:0 0 6px;color:#94a3b8;font-size:12px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Email</p>
                    <a href="mailto:{safe_email}" style="color:#818cf8;font-size:16px;text-decoration:none;">{safe_email}</a>
                  </td>
                </tr>
                <tr>
                  <td style="padding-bottom:32px;">
                    <p style="margin:0 0 10px;color:#94a3b8;font-size:12px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Message</p>
                    <div style="background:#0f172a;border-left:4px solid #6366f1;border-radius:8px;padding:20px;color:#cbd5e1;font-size:15px;line-height:1.7;">
                      {safe_message}
                    </div>
                  </td>
                </tr>
                <tr>
                  <td>
                    <a href="mailto:{safe_email}?subject=Re: Your enquiry to ExpertiseCo"
                       style="display:inline-block;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;padding:14px 28px;border-radius:10px;text-decoration:none;font-weight:600;font-size:14px;">
                      Reply to {safe_name} →
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="background:#0f172a;padding:20px 40px;border-top:1px solid #1e293b;">
              <p style="margin:0;color:#475569;font-size:12px;text-align:center;">
                ExpertiseCo CRM · Auto-generated notification · ID {enquiry.id}
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def _confirmation_html(enquiry) -> str:
    """HTML body for submitter confirmation email."""
    safe_name = html.escape(enquiry.name)
    safe_message = html.escape(enquiry.message)
    truncated = safe_message[:300] + ('...' if len(safe_message) > 300 else '')
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>We received your message — ExpertiseCo</title>
</head>
<body style="margin:0;padding:0;background:#0f172a;font-family:'Segoe UI',Roboto,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f172a;padding:40px 20px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="background:#1e293b;border-radius:16px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.4);">
          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#10b981,#059669);padding:32px 40px;text-align:center;">
              <div style="width:64px;height:64px;background:rgba(255,255,255,0.15);border-radius:50%;margin:0 auto 16px;display:flex;align-items:center;justify-content:center;font-size:32px;">
                ✅
              </div>
              <h1 style="margin:0;color:#fff;font-size:26px;font-weight:700;">
                Message Received!
              </h1>
              <p style="margin:10px 0 0;color:rgba(255,255,255,0.8);font-size:15px;">
                Thank you for reaching out to ExpertiseCo.
              </p>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding:40px;">
              <p style="color:#cbd5e1;font-size:16px;line-height:1.7;margin:0 0 24px;">
                Hi <strong style="color:#f1f5f9;">{safe_name}</strong>,
              </p>
              <p style="color:#94a3b8;font-size:15px;line-height:1.7;margin:0 0 24px;">
                We've successfully received your enquiry and our team will review it shortly.
                You can expect a response within <strong style="color:#10b981;">1 business day</strong>.
              </p>
              <!-- Message recap -->
              <div style="background:#0f172a;border-radius:12px;padding:24px;margin-bottom:32px;">
                <p style="margin:0 0 12px;color:#475569;font-size:12px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Your Message</p>
                <p style="margin:0;color:#94a3b8;font-size:14px;line-height:1.7;font-style:italic;">
                  "{truncated}"
                </p>
              </div>
              <!-- Contact info -->
              <div style="border-top:1px solid #334155;padding-top:24px;">
                <p style="margin:0 0 8px;color:#94a3b8;font-size:14px;">Questions? Reach us directly:</p>
                <a href="mailto:consult@expertiseco.com" style="color:#6366f1;text-decoration:none;font-size:14px;">
                  consult@expertiseco.com
                </a>
              </div>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="background:#0f172a;padding:20px 40px;border-top:1px solid #1e293b;text-align:center;">
              <p style="margin:0;color:#475569;font-size:12px;">
                © 2024 ExpertiseCo · Manhattan Corporate HQ, NYC
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


# ─── Email Senders ─────────────────────────────────────────────────────────────

_PLACEHOLDER_VALUES = {
    '', 'your-app-password-here', 'your.gmail@gmail.com',
    'xxxx-xxxx-xxxx-xxxx', 'your-password',
}


def _is_email_configured() -> bool:
    """
    Returns True only if real SMTP credentials are set.
    Prevents crash when .env still has placeholder values.
    """
    user = getattr(settings, 'EMAIL_HOST_USER', '').strip().lower()
    pwd = getattr(settings, 'EMAIL_HOST_PASSWORD', '').strip().lower()
    return (
        bool(user) and user not in _PLACEHOLDER_VALUES and
        bool(pwd) and pwd not in _PLACEHOLDER_VALUES
    )


def send_notification_email(enquiry) -> bool:
    """
    Send admin notification email when a new enquiry is submitted.
    Returns True on success, False on failure (never raises).
    """
    # Guard: skip if SMTP not configured
    if not _is_email_configured():
        logger.warning(
            "Admin notification skipped — EMAIL_HOST_USER or EMAIL_HOST_PASSWORD "
            "not configured in .env. Set your Gmail App Password to enable emails."
        )
        return False

    try:
        subject = f"[New Enquiry] {enquiry.name} — ExpertiseCo CRM"
        plain_text = (
            f"New Enquiry Received\n"
            f"{'=' * 40}\n"
            f"Name:    {enquiry.name}\n"
            f"Email:   {enquiry.email}\n"
            f"Message: {enquiry.message}\n"
            f"{'=' * 40}\n"
            f"Submitted at: {enquiry.created_at}\n"
        )

        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.NOTIFICATION_EMAIL],
            reply_to=[enquiry.email],
        )
        msg.attach_alternative(_notification_html(enquiry), "text/html")
        msg.send(fail_silently=False)

        logger.info(f"Admin notification sent for enquiry {enquiry.id} from {enquiry.email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send admin notification for enquiry {enquiry.id}: {e}")
        return False


def send_confirmation_email(enquiry) -> bool:
    """
    Send a confirmation email to the person who submitted the form.
    Returns True on success, False on failure (never raises).
    """
    # Guard: skip if SMTP not configured
    if not _is_email_configured():
        logger.warning(
            "Confirmation email skipped — EMAIL_HOST_USER or EMAIL_HOST_PASSWORD "
            "not configured in .env."
        )
        return False

    try:
        subject = "We received your message — ExpertiseCo"
        plain_text = (
            f"Hi {enquiry.name},\n\n"
            f"Thank you for contacting ExpertiseCo!\n\n"
            f"We've received your message and will respond within 1 business day.\n\n"
            f"Your message:\n\"{enquiry.message}\"\n\n"
            f"Best regards,\n"
            f"The ExpertiseCo Team\n"
            f"consult@expertiseco.com"
        )

        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[enquiry.email],
        )
        msg.attach_alternative(_confirmation_html(enquiry), "text/html")
        msg.send(fail_silently=False)

        logger.info(f"Confirmation email sent to {enquiry.email} for enquiry {enquiry.id}")
        return True

    except Exception as e:
        logger.error(f"Failed to send confirmation email to {enquiry.email}: {e}")
        return False