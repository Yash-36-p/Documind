import uuid
import os
from django.db import models
from django.conf import settings

def document_upload_path(instance, filename):
    return f"documents/{instance.id}/{filename}"

def preview_upload_path(instance, filename):
    return f"previews/{instance.id}/{filename}"

class Document(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    class Category(models.TextChoices):
        INVOICE = 'invoice', 'Invoice'
        RECEIPT = 'receipt', 'Receipt'
        RESUME = 'resume', 'Resume / CV'
        ID_CARD = 'id_card', 'ID Document'
        CONTRACT = 'contract', 'Contract / Agreement'
        CERTIFICATE = 'certificate', 'Certificate'
        FORM = 'form', 'Form'
        REPORT = 'report', 'Report'
        OTHER = 'other', 'Other'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to=document_upload_path)
    preview_image = models.ImageField(upload_to=preview_upload_path, null=True, blank=True)
    file_type = models.CharField(max_length=30, default='pdf') # pdf, png, jpg, jpeg
    mime_type = models.CharField(max_length=100, default='application/pdf')
    file_size = models.BigIntegerField(default=0) # in bytes
    page_count = models.PositiveIntegerField(default=1)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    error_message = models.TextField(blank=True, default='')

    # Classification
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        default=Category.OTHER,
        db_index=True
    )
    classification_confidence = models.FloatField(default=0.0) # 0 to 100
    classification_explanation = models.JSONField(default=dict, blank=True)

    # OCR extraction summary
    ocr_confidence = models.FloatField(default=0.0) # 0 to 100
    raw_text = models.TextField(blank=True, default='')

    # Verification / Manual Review
    is_verified = models.BooleanField(default=False, db_index=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_documents'
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    # Metadata & Timing
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_documents'
    )
    processing_time_ms = models.IntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    @property
    def filename(self):
        return os.path.basename(self.file.name) if self.file else self.title


class DocumentPage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='pages')
    page_number = models.PositiveIntegerField()
    text = models.TextField(blank=True, default='')
    ocr_confidence = models.FloatField(default=0.0)
    extraction_method = models.CharField(max_length=50, default='pymupdf') # pymupdf, tesseract
    thumbnail = models.ImageField(upload_to=preview_upload_path, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['page_number']
        unique_together = ('document', 'page_number')

    def __str__(self):
        return f"{self.document.title} - Page {self.page_number}"

