from django.db import models
from django.conf import settings
from apps.documents.models import Document

class ExtractedField(models.Model):
    """
    Extracted key-value pairs and confidence scores from document OCR.
    """
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

    id = models.BigAutoField(primary_key=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='extracted_fields')
    
    # Core fields requested by user
    field_name = models.CharField(max_length=150, db_index=True, help_text="e.g. Invoice Number, Vendor, Total Amount")
    extracted_value = models.TextField(blank=True, default='', help_text="Extracted text or normalized value")
    confidence = models.FloatField(default=0.0, help_text="Estimated confidence score (0-100%)")

    # Tracking & Correction metadata
    field_key = models.CharField(max_length=100, db_index=True)
    field_type = models.CharField(max_length=30, choices=FieldType.choices, default=FieldType.STRING)
    is_corrected = models.BooleanField(default=False)
    original_value = models.TextField(blank=True, default='')
    page_number = models.PositiveIntegerField(default=1)
    bounding_box = models.JSONField(default=dict, blank=True)
    context_snippet = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['page_number', 'field_name']

    def __str__(self):
        return f"{self.document.filename} - {self.field_name}: {self.extracted_value} ({self.confidence}%)"

    # Aliases for compatibility
    @property
    def field_label(self):
        return self.field_name

    @field_label.setter
    def field_label(self, val):
        self.field_name = val

    @property
    def field_value(self):
        return self.extracted_value

    @field_value.setter
    def field_value(self, val):
        self.extracted_value = val


# Compatibility alias
DocumentField = ExtractedField


class FieldCorrectionHistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='correction_logs')
    extracted_field = models.ForeignKey(
        ExtractedField,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='history'
    )
    field_name = models.CharField(max_length=150)
    field_key = models.CharField(max_length=100, blank=True)
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
        return f"Correction on {self.field_name}: '{self.previous_value}' -> '{self.new_value}'"
