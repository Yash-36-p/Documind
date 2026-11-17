import uuid
from django.db import models
from django.conf import settings
from apps.documents.models import Document

class DocumentField(models.Model):
    class FieldType(models.TextChoices):
        STRING = 'string', 'Text'
        NUMBER = 'number', 'Number'
        CURRENCY = 'currency', 'Currency / Amount'
        DATE = 'date', 'Date'
        EMAIL = 'email', 'Email'
        PHONE = 'phone', 'Phone Number'
        ADDRESS = 'address', 'Address'
        NAME = 'name', 'Person / Contact'
        ORGANIZATION = 'organization', 'Organization / Company'
        ID_NUMBER = 'id_number', 'ID / Ref Number'
        OTHER = 'other', 'Other'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='fields')
    field_key = models.CharField(max_length=100, db_index=True)
    field_label = models.CharField(max_length=150)
    field_value = models.TextField(blank=True, default='')
    original_value = models.TextField(blank=True, default='')
    confidence = models.FloatField(default=0.0) # 0 to 100
    field_type = models.CharField(max_length=30, choices=FieldType.choices, default=FieldType.STRING)

    is_corrected = models.BooleanField(default=False)
    page_number = models.PositiveIntegerField(default=1)
    bounding_box = models.JSONField(default=dict, blank=True)
    context_snippet = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['page_number', 'field_key']

    def __str__(self):
        return f"{self.document.title} - {self.field_label}: {self.field_value}"


class FieldCorrectionHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='correction_logs')
    document_field = models.ForeignKey(
        DocumentField,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='history'
    )
    field_key = models.CharField(max_length=100)
    field_label = models.CharField(max_length=150, blank=True)
    previous_value = models.TextField(blank=True, default='')
    new_value = models.TextField(blank=True, default='')
    corrected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='field_corrections'
    )
    corrected_at = models.DateTimeField(auto_now_add=True)
    correction_type = models.CharField(
        max_length=50,
        default='manual_edit'
    ) # manual_edit, field_added, field_deleted, classification_override
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-corrected_at']

    def __str__(self):
        return f"Correction on {self.field_key}: '{self.previous_value}' -> '{self.new_value}'"

