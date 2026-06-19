"""
DRF Serializers for the Enquiry MongoEngine document.
Since MongoEngine docs aren't Django models, we use plain Serializers.
"""
from rest_framework import serializers


class EnquiryCreateSerializer(serializers.Serializer):
    """
    Used for public contact form submission (POST /api/contact/).
    Validates name, email, and message from the client.
    """
    name = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    message = serializers.CharField(min_length=10)

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        return value

    def validate_message(self, value):
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long.")
        return value


def enquiry_to_dict(enquiry) -> dict:
    """Serialize a MongoEngine Enquiry document to a dict."""
    status_display = {'new': 'New', 'read': 'Read', 'replied': 'Replied'}
    return {
        'id': str(enquiry.id),
        'name': enquiry.name,
        'email': enquiry.email,
        'message': enquiry.message,
        'status': enquiry.status,
        'status_display': status_display.get(enquiry.status, enquiry.status),
        'created_at': enquiry.created_at.strftime('%Y-%m-%d %H:%M:%S') if enquiry.created_at else None,
        'updated_at': enquiry.updated_at.strftime('%Y-%m-%d %H:%M:%S') if enquiry.updated_at else None,
        'ip_address': enquiry.ip_address,
        'notification_sent': enquiry.notification_sent,
        'confirmation_sent': enquiry.confirmation_sent,
    }


class AdminLoginSerializer(serializers.Serializer):
    """Serializer for admin login credentials."""
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(
        max_length=128,
        style={'input_type': 'password'},
        write_only=True,
    )


class EnquiryUpdateSerializer(serializers.Serializer):
    """Used by admin to update status only."""
    status = serializers.ChoiceField(choices=['new', 'read', 'replied'])