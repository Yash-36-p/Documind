import os
import io
import logging
from celery import shared_task
from django.core.files.base import ContentFile
from apps.documents.models import Document, DocumentPage, ProcessingLog
from apps.ocr.engine import OcrEngine
from apps.classification.classifier import DocumentClassifier
from apps.extraction.extractor import InformationExtractor
from apps.extraction.models import ExtractedField
from apps.audit.utils import log_activity
from apps.audit.models import AuditLog

logger = logging.getLogger(__name__)

# Map internal classification codes to Document.DocumentType choices
DOC_TYPE_MAP = {
    'invoice': Document.DocumentType.INVOICE,
    'receipt': Document.DocumentType.RECEIPT,
    'resume': Document.DocumentType.RESUME,
    'id_card': Document.DocumentType.ID_DOCUMENT,
    'contract': Document.DocumentType.CONTRACT,
    'certificate': Document.DocumentType.CERTIFICATE,
    'form': Document.DocumentType.FORM,
    'report': Document.DocumentType.REPORT,
    'other': Document.DocumentType.OTHER,
}

def run_document_processing(document_id):
    """
    Main execution pipeline for document processing.
    Emits ProcessingLog entries at each step.
    """
    try:
        doc = Document.objects.get(id=document_id)
    except Document.DoesNotExist:
        logger.error(f"Document #{document_id} not found for processing.")
        return False

    doc.status = Document.Status.PROCESSING
    doc.error_message = ''
    doc.save(update_fields=['status', 'error_message'])

    ProcessingLog.objects.create(
        document=doc,
        log_level=ProcessingLog.Level.INFO,
        stage='PIPELINE_START',
        message=f"Initiated processing for {doc.filename} ({doc.file_type.upper()})"
    )

    log_activity(AuditLog.Action.PROCESS_START, document=doc, details={"stage": "started"})

    try:
        file_path = doc.file.path
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File at {file_path} does not exist on disk.")

        # Stage 1: OCR Extraction
        ProcessingLog.objects.create(
            document=doc,
            log_level=ProcessingLog.Level.INFO,
            stage='OCR_EXTRACTION',
            message=f"Starting OCR extraction on {doc.filename}"
        )

        ocr_result = OcrEngine.process_file(file_path, file_type=doc.file_type)

        doc.raw_text = ocr_result.get('full_text', '')
        doc.ocr_confidence = ocr_result.get('overall_confidence', 0.0)
        doc.page_count = ocr_result.get('page_count', 1)
        doc.processing_time_ms = ocr_result.get('elapsed_ms', 0)

        # Thumbnail generation
        first_thumb = ocr_result.get('first_page_thumb_bytes')
        if first_thumb and not doc.preview_image:
            doc.preview_image.save(
                f"{doc.id}_preview.jpg",
                ContentFile(first_thumb),
                save=False
            )

        # Store DocumentPage records
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

        ProcessingLog.objects.create(
            document=doc,
            log_level=ProcessingLog.Level.INFO,
            stage='OCR_EXTRACTION',
            message=f"Extracted {len(doc.raw_text)} characters across {doc.page_count} pages with {doc.ocr_confidence}% OCR quality."
        )

        # Stage 2: Document Classification
        classification = DocumentClassifier.classify(doc.raw_text)
        detected_category = classification.get('category', 'other')
        doc.document_type = DOC_TYPE_MAP.get(detected_category, Document.DocumentType.OTHER)
        doc.classification_confidence = classification.get('confidence', 50.0)
        doc.classification_explanation = classification.get('explanation', {})

        ProcessingLog.objects.create(
            document=doc,
            log_level=ProcessingLog.Level.INFO,
            stage='CLASSIFICATION',
            message=f"Classified as '{doc.document_type}' ({doc.classification_confidence}% confidence)",
            details=doc.classification_explanation
        )

        # Stage 3: Information Extraction
        extracted_fields = InformationExtractor.extract_fields(
            doc.raw_text,
            category=detected_category
        )

        # Retain manually corrected fields
        existing_corrected_fields = {
            f.field_name: f for f in doc.extracted_fields.filter(is_corrected=True)
        }
        # Clear uncorrected fields
        doc.extracted_fields.filter(is_corrected=False).delete()

        new_fields = []
        confidences = [doc.ocr_confidence]

        for ef in extracted_fields:
            name = ef.get('field_label', ef.get('field_name', 'Field'))
            val = ef.get('field_value', ef.get('extracted_value', ''))
            conf = float(ef.get('confidence', 80.0))
            confidences.append(conf)

            if name not in existing_corrected_fields:
                new_fields.append(ExtractedField(
                    document=doc,
                    field_name=name,
                    extracted_value=val,
                    confidence=conf,
                    field_key=ef.get('field_key', name.lower().replace(' ', '_')),
                    field_type=ef.get('field_type', 'string'),
                    context_snippet=ef.get('context_snippet', ''),
                    original_value=val,
                    is_corrected=False,
                    page_number=1
                ))

        if new_fields:
            ExtractedField.objects.bulk_create(new_fields)

        # Compute overall document confidence estimate
        if confidences:
            doc.confidence = round(sum(confidences) / len(confidences), 1)
        else:
            doc.confidence = doc.ocr_confidence

        doc.status = Document.Status.COMPLETED
        doc.save()

        ProcessingLog.objects.create(
            document=doc,
            log_level=ProcessingLog.Level.INFO,
            stage='COMPLETED',
            message=f"Processing successfully completed. Overall confidence: {doc.confidence}%. {len(extracted_fields)} fields extracted."
        )

        log_activity(
            AuditLog.Action.PROCESS_SUCCESS,
            document=doc,
            details={
                "document_type": doc.document_type,
                "confidence": doc.confidence,
                "ocr_confidence": doc.ocr_confidence,
                "fields_extracted": len(extracted_fields),
                "pages": doc.page_count,
                "time_ms": doc.processing_time_ms
            }
        )
        return True

    except Exception as e:
        logger.exception(f"Document processing failed for #{document_id}: {e}")
        doc.status = Document.Status.FAILED
        doc.error_message = str(e)
        doc.save(update_fields=['status', 'error_message'])

        ProcessingLog.objects.create(
            document=doc,
            log_level=ProcessingLog.Level.ERROR,
            stage='PIPELINE_ERROR',
            message=f"Processing error: {str(e)}"
        )

        log_activity(
            AuditLog.Action.PROCESS_FAIL,
            document=doc,
            details={"error": str(e)}
        )
        return False


@shared_task(bind=True, max_retries=2)
def process_document_task(self, document_id):
    """
    Celery background worker task.
    """
    return run_document_processing(document_id)
