import uuid
from django.db import models
from django.conf import settings
from apps.documents.models import Document

class AuditLog(models.Model):
    class Action(models.TextChoices):
        UPLOAD = 'UPLOAD', 'Document Uploaded'
        PROCESS_START = 'PROCESS_START', 'Processing Started'
        PROCESS_SUCCESS = 'PROCESS_SUCCESS', 'Processing Completed'
        PROCESS_FAIL = 'PROCESS_FAIL', 'Processing Failed'
        FIELD_EDIT = 'FIELD_EDIT', 'Field Value Corrected'
        FIELD_CREATE = 'FIELD_CREATE', 'Field Created'
        FIELD_DELETE = 'FIELD_DELETE', 'Field Deleted'
        CLASSIFICATION_CHANGE = 'CLASSIFICATION_CHANGE', 'Classification Changed'
        VERIFY = 'VERIFY', 'Document Verified'
        DELETE = 'DELETE', 'Document Deleted'
        EXPORT = 'EXPORT', 'Exported to CSV'
        LOGIN = 'LOGIN', 'User Logged In'
        REGISTER = 'REGISTER', 'User Registered'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    user_name = models.CharField(max_length=150, blank=True, default='')
    action = models.CharField(max_length=50, choices=Action.choices, db_index=True)
    document = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_entries'
    )
    document_title = models.CharField(max_length=255, blank=True, default='')
    ip_address = models.CharField(max_length=50, blank=True, default='')
    user_agent = models.CharField(max_length=255, blank=True, default='')
    details = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {self.user_name or 'System'} - {self.get_action_display()}"

