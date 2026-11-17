import os
import io
import logging
from celery import shared_task
from django.core.files.base import ContentFile
from apps.documents.models import Document, DocumentPage
from apps.ocr.engine import OcrEngine
from apps.classification.classifier import DocumentClassifier
from apps.extraction.extractor import InformationExtractor
from apps.extraction.models import DocumentField
from apps.audit.utils import log_activity
from apps.audit.models import AuditLog

logger = logging.getLogger(__name__)

def run_document_processing(document_id: str):
    """
    Main execution pipeline for document processing.
    Can be run synchronously or via Celery task.
    """
    try:
        doc = Document.objects.get(id=document_id)
    except Document.DoesNotExist:
        logger.error(f"Document {document_id} not found for processing.")
        return False

    doc.status = Document.Status.PROCESSING
    doc.error_message = ''
    doc.save(update_fields=['status', 'error_message'])
    log_activity(AuditLog.Action.PROCESS_START, document=doc, details={"stage": "started"})

    try:
        file_path = doc.file.path
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File at {file_path} does not exist on disk.")

        # 1. OCR Extraction (PyMuPDF for digital PDF + Tesseract for scanned / images)
        ocr_result = OcrEngine.process_file(file_path, file_type=doc.file_type)

        doc.raw_text = ocr_result.get('full_text', '')
        doc.ocr_confidence = ocr_result.get('overall_confidence', 0.0)
        doc.page_count = ocr_result.get('page_count', 1)
        doc.processing_time_ms = ocr_result.get('elapsed_ms', 0)

        # Save first page thumbnail for preview if available
        first_thumb = ocr_result.get('first_page_thumb_bytes')
        if first_thumb and not doc.preview_image:
            doc.preview_image.save(
                f"{doc.id}_preview.jpg",
                ContentFile(first_thumb),
                save=False
            )

        # 2. Re-create DocumentPage objects
        doc.pages.all().delete()
        for p_data in ocr_result.get('pages', []):
            page_obj = DocumentPage(
                document=doc,
                page_number=p_data['page_number'],
                text=p_data['text'],
                ocr_confidence=p_data['ocr_confidence'],
                extraction_method=p_data['extraction_method'],
                metadata={
                    'char_count': p_data['char_count'],
                    'word_count': p_data['word_count']
                }
            )
            if p_data.get('thumbnail_bytes'):
                page_obj.thumbnail.save(
                    f"{doc.id}_p{p_data['page_number']}.jpg",
                    ContentFile(p_data['thumbnail_bytes']),
                    save=False
                )
            page_obj.save()

        # 3. Document Classification
        classification = DocumentClassifier.classify(doc.raw_text)
        doc.category = classification['category']
        doc.classification_confidence = classification['confidence']
        doc.classification_explanation = classification['explanation']

        # 4. Information Extraction
        extracted_fields = InformationExtractor.extract_fields(
            doc.raw_text,
            category=doc.category
        )

        # Retain manually corrected fields if this is a re-run
        existing_corrected_fields = {
            f.field_key: f for f in doc.fields.filter(is_corrected=True)
        }
        # Delete uncorrected fields
        doc.fields.filter(is_corrected=False).delete()

        # Insert new fields
        new_fields = []
        for ef in extracted_fields:
            if ef['field_key'] not in existing_corrected_fields:
                new_fields.append(DocumentField(
                    document=doc,
                    field_key=ef['field_key'],
                    field_label=ef['field_label'],
                    field_value=ef['field_value'],
                    original_value=ef['original_value'],
                    confidence=ef['confidence'],
                    field_type=ef['field_type'],
                    context_snippet=ef.get('context_snippet', ''),
                    is_corrected=False,
                    page_number=1
                ))

        if new_fields:
            DocumentField.objects.bulk_create(new_fields)

        doc.status = Document.Status.COMPLETED
        doc.save()

        log_activity(
            AuditLog.Action.PROCESS_SUCCESS,
            document=doc,
            details={
                "category": doc.category,
                "confidence": doc.classification_confidence,
                "ocr_confidence": doc.ocr_confidence,
                "fields_extracted": len(extracted_fields),
                "pages": doc.page_count,
                "time_ms": doc.processing_time_ms
            }
        )
        return True

    except Exception as e:
        logger.exception(f"Document processing failed for {document_id}: {e}")
        doc.status = Document.Status.FAILED
        doc.error_message = str(e)
        doc.save(update_fields=['status', 'error_message'])
        log_activity(
            AuditLog.Action.PROCESS_FAIL,
            document=doc,
            details={"error": str(e)}
        )
        return False


@shared_task(bind=True, max_retries=2)
def process_document_task(self, document_id: str):
    """
    Celery background worker task.
    """
    return run_document_processing(document_id)
