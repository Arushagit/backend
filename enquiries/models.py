"""
Enquiry document model using MongoEngine.
Stores contact form submissions directly in MongoDB.

MongoEngine is used instead of Django ORM because:
- Django ORM requires sqlparse 0.2.4 (via djongo) which conflicts with Django 4.2
- MongoEngine works natively with pymongo 4.x and Django 4.2
- Provides cleaner MongoDB document semantics
"""
import datetime
import mongoengine as me


class Enquiry(me.Document):
    """
    MongoDB document representing a contact form submission.
    Stored in the 'enquiry' collection.
    """
    STATUS_CHOICES = ('new', 'read', 'replied')

    name = me.StringField(max_length=200, required=True)
    email = me.EmailField(required=True)
    message = me.StringField(required=True)
    status = me.StringField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
    )
    created_at = me.DateTimeField(default=datetime.datetime.utcnow)
    updated_at = me.DateTimeField(default=datetime.datetime.utcnow)
    ip_address = me.StringField(max_length=45, null=True)
    notification_sent = me.BooleanField(default=False)
    confirmation_sent = me.BooleanField(default=False)

    meta = {
        'collection': 'enquiries',
        'ordering': ['-created_at'],
        'indexes': ['status', 'email', '-created_at'],
    }

    def save(self, *args, **kwargs):
        """Auto-update updated_at on every save."""
        self.updated_at = datetime.datetime.utcnow()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.status.upper()}] {self.name} <{self.email}>"