import os
from django.db import models
from django.conf import settings

def document_upload_path(instance, filename):
    return f"documents/{instance.id}/{filename}"

def preview_upload_path(instance, filename):
    return f"previews/{instance.id}/{filename}"

class Document(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    class DocumentType(models.TextChoices):
        INVOICE = 'Invoice', 'Invoice'
        RECEIPT = 'Receipt', 'Receipt'
        RESUME = 'Resume / CV', 'Resume / CV'
        ID_DOCUMENT = 'ID Document', 'ID Document'
        CONTRACT = 'Contract', 'Contract / Agreement'
        CERTIFICATE = 'Certificate', 'Certificate'
        FORM = 'Form', 'Form'
        REPORT = 'Report', 'Report'
        OTHER = 'Other', 'Other'

    # Auto-incrementing Integer ID (e.g. 101, 102...)
    id = models.BigAutoField(primary_key=True)
    filename = models.CharField(max_length=255, db_index=True)
    title = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to=document_upload_path)
    preview_image = models.ImageField(upload_to=preview_upload_path, null=True, blank=True)

    document_type = models.CharField(
        max_length=50,
        choices=DocumentType.choices,
        default=DocumentType.OTHER,
        db_index=True
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )

    # Confidence scores (estimates based on extraction rules & validation)
    confidence = models.FloatField(default=0.0, help_text="Overall confidence score (0-100%)")
    ocr_confidence = models.FloatField(default=0.0)
    classification_confidence = models.FloatField(default=0.0)
    classification_explanation = models.JSONField(default=dict, blank=True)

    raw_text = models.TextField(blank=True, default='')
    file_type = models.CharField(max_length=30, default='pdf')
    mime_type = models.CharField(max_length=100, default='application/pdf')
    file_size = models.BigIntegerField(default=0)
    page_count = models.PositiveIntegerField(default=1)
    error_message = models.TextField(blank=True, default='')

    # Human Verification
    is_verified = models.BooleanField(default=False, db_index=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_documents'
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    # Ownership & Timestamps
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_documents'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    processing_time_ms = models.IntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"[{self.id}] {self.filename} ({self.get_status_display()})"

    # Aliases for compatibility
    @property
    def category(self):
        return self.document_type

    @category.setter
    def category(self, val):
        self.document_type = val

    @property
    def created_at(self):
        return self.uploaded_at

    @property
    def category_display(self):
        return self.get_document_type_display()


class DocumentPage(models.Model):
    id = models.BigAutoField(primary_key=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='pages')
    page_number = models.PositiveIntegerField()
    text = models.TextField(blank=True, default='', help_text="Page-wise extracted text")
    ocr_confidence = models.FloatField(default=0.0)
    extraction_method = models.CharField(max_length=50, default='pymupdf')
    thumbnail = models.ImageField(upload_to=preview_upload_path, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['page_number']
        unique_together = ('document', 'page_number')

    def __str__(self):
        return f"{self.document.filename} - Page {self.page_number}"


class ProcessingLog(models.Model):
    """
    Tracks processing events, warnings, errors and stage progress for documents.
    """
    class Level(models.TextChoices):
        INFO = 'INFO', 'Info'
        WARNING = 'WARNING', 'Warning'
        ERROR = 'ERROR', 'Error'

    id = models.BigAutoField(primary_key=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='processing_logs')
    log_level = models.CharField(max_length=10, choices=Level.choices, default=Level.INFO)
    stage = models.CharField(max_length=50) # e.g. OCR_EXTRACTION, CLASSIFICATION, FIELD_EXTRACTION
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.log_level}] Doc #{self.document.id} ({self.stage}): {self.message}"
