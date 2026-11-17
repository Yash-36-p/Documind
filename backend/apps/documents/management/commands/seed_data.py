import os
import io
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils import timezone
import pymupdf as fitz
from PIL import Image, ImageDraw

from apps.documents.models import Document, DocumentPage, ProcessingLog
from apps.extraction.models import ExtractedField
from apps.documents.tasks import run_document_processing

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds initial users and sample documents matching the specification for DocuMind'

    def handle(self, *args, **options):
        self.stdout.write("Seeding DocuMind demo users...")

        # 1. Admin user
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@documind.ai',
                'first_name': 'Sarah',
                'last_name': 'Connor',
                'role': User.Role.ADMIN,
                'organization': 'DocuMind HQ',
                'is_staff': True,
                'is_superuser': True
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()

        # 2. Reviewer user (User 1)
        reviewer_user, _ = User.objects.get_or_create(
            username='reviewer',
            defaults={
                'email': 'reviewer@documind.ai',
                'first_name': 'User',
                'last_name': '1',
                'role': User.Role.REVIEWER,
                'organization': 'ABC Technologies'
            }
        )
        reviewer_user.set_password('reviewer123')
        reviewer_user.save()

        # 3. Viewer user
        viewer_user, _ = User.objects.get_or_create(
            username='viewer',
            defaults={
                'email': 'viewer@documind.ai',
                'first_name': 'Taylor',
                'last_name': 'Brooks',
                'role': User.Role.VIEWER,
                'organization': 'Compliance Partners'
            }
        )
        viewer_user.set_password('viewer123')
        viewer_user.save()

        self.stdout.write("Users ready: admin, reviewer (User 1), viewer.")

        # Seed sample documents if table is empty
        if Document.objects.count() == 0:
            self.stdout.write("Generating sample documents matching specification...")

            # Document 101: invoice_001.pdf
            pdf_bytes = self._create_invoice_001_pdf()
            doc101 = Document.objects.create(
                id=101,
                filename='invoice_001.pdf',
                title='ABC Technologies Invoice',
                document_type=Document.DocumentType.INVOICE,
                status=Document.Status.COMPLETED,
                confidence=94.0,
                ocr_confidence=97.0,
                classification_confidence=98.5,
                uploaded_by=reviewer_user,
                file_type='pdf',
                mime_type='application/pdf',
                page_count=1,
                raw_text="""ABC TECHNOLOGIES PVT LTD
Building 4, Cyber City, Phase III, Gurugram, India
contact@abctechnologies.com | +91 124 555 0192

TAX INVOICE

Invoice Number: INV-2026-001
Invoice Date: 15-11-2026
Vendor: ABC Technologies
Due Date: 30-11-2026

Billed To:
Zenith Solutions International
Attn: Accounts Payable
Floor 5, Innovation Hub, Bengaluru

Line Items:
1. Enterprise Cloud Computing Subscription (1 Month): ₹20,000
2. Managed Security & Threat Protection SLA: ₹5,000

Subtotal: ₹25,000
Tax / GST (0% Reverse Charge): ₹0
Total Amount: ₹25,000

Thank you for choosing ABC Technologies!"""
            )
            doc101.file.save('invoice_001.pdf', ContentFile(pdf_bytes), save=False)
            doc101.file_size = len(pdf_bytes)
            doc101.save()

            # Create ExtractedField records matching example:
            # Invoice Number: INV-2026-001 (98%)
            # Vendor: ABC Technologies (95%)
            # Invoice Date: 15-11-2026 (97%)
            # Total Amount: ₹25,000 (96%)
            fields_data = [
                ('Invoice Number', 'INV-2026-001', 98.0, 'invoice_number', 'id_number'),
                ('Vendor', 'ABC Technologies', 95.0, 'vendor', 'organization'),
                ('Invoice Date', '15-11-2026', 97.0, 'invoice_date', 'date'),
                ('Total Amount', '₹25,000', 96.0, 'total_amount', 'currency'),
                ('Due Date', '30-11-2026', 92.0, 'due_date', 'date'),
                ('Email', 'contact@abctechnologies.com', 95.0, 'email', 'email'),
            ]
            for fname, val, conf, fkey, ftype in fields_data:
                ExtractedField.objects.create(
                    document=doc101,
                    field_name=fname,
                    extracted_value=val,
                    confidence=conf,
                    field_key=fkey,
                    field_type=ftype,
                    original_value=val
                )

            # ProcessingLog entries for Document 101
            ProcessingLog.objects.create(
                document=doc101,
                log_level=ProcessingLog.Level.INFO,
                stage='OCR_EXTRACTION',
                message="Extracted 840 characters using PyMuPDF direct engine (OCR quality: 97%)."
            )
            ProcessingLog.objects.create(
                document=doc101,
                log_level=ProcessingLog.Level.INFO,
                stage='CLASSIFICATION',
                message="Document identified as 'Invoice' with 98.5% confidence score."
            )
            ProcessingLog.objects.create(
                document=doc101,
                log_level=ProcessingLog.Level.INFO,
                stage='FIELD_EXTRACTION',
                message="Extracted 6 fields with average confidence of 94% (rule-based validation passed)."
            )

            # Render page thumbnail
            doc_fitz = fitz.open(stream=pdf_bytes, filetype="pdf")
            pix = doc_fitz[0].get_pixmap(dpi=150)
            thumb_bytes = pix.tobytes("png")
            doc101.preview_image.save('invoice_001_thumb.png', ContentFile(thumb_bytes))
            DocumentPage.objects.create(
                document=doc101,
                page_number=1,
                text=doc101.raw_text,
                ocr_confidence=97.0,
                extraction_method='pymupdf_direct'
            )
            doc_fitz.close()
            self.stdout.write(self.style.SUCCESS("Created Document #101 (invoice_001.pdf) with exact sample fields!"))

            # Document 102: Resume
            resume_bytes = self._create_resume_pdf()
            doc102 = Document.objects.create(
                id=102,
                filename='resume_elena_rostova.pdf',
                title='Elena Rostova Senior AI Engineer Resume',
                document_type=Document.DocumentType.RESUME,
                status=Document.Status.COMPLETED,
                confidence=96.0,
                ocr_confidence=98.0,
                classification_confidence=99.0,
                uploaded_by=reviewer_user,
                file_type='pdf',
                mime_type='application/pdf',
                page_count=1,
                raw_text="""Elena Rostova
Senior AI & Machine Learning Engineer
elena.rostova.ml@gmail.com | (206) 555-8392 | Seattle, WA

PROFESSIONAL SUMMARY
Machine Learning Engineer with 7+ years developing scalable OCR and NLP pipelines.

EDUCATION
Master of Science in Computer Science, Stanford University (2019)
Bachelor of Science in Software Engineering, University of Washington (2017)

SKILLS & TECHNOLOGIES
Python, PyTorch, React, Django REST Framework, Tesseract OCR, PyMuPDF, Celery, PostgreSQL."""
            )
            doc102.file.save('resume_elena_rostova.pdf', ContentFile(resume_bytes), save=False)
            doc102.file_size = len(resume_bytes)
            doc102.save()

            ExtractedField.objects.create(document=doc102, field_name='Candidate Name', extracted_value='Elena Rostova', confidence=96.0, field_key='candidate_name', field_type='name')
            ExtractedField.objects.create(document=doc102, field_name='Email', extracted_value='elena.rostova.ml@gmail.com', confidence=98.0, field_key='email', field_type='email')
            ExtractedField.objects.create(document=doc102, field_name='Phone', extracted_value='(206) 555-8392', confidence=94.0, field_key='phone', field_type='phone')
            ExtractedField.objects.create(document=doc102, field_name='Degree', extracted_value='Master of Science in Computer Science', confidence=95.0, field_key='degree', field_type='string')

            # Thumbnail
            doc_fitz = fitz.open(stream=resume_bytes, filetype="pdf")
            pix = doc_fitz[0].get_pixmap(dpi=150)
            doc102.preview_image.save('resume_thumb.png', ContentFile(pix.tobytes("png")))
            DocumentPage.objects.create(
                document=doc102,
                page_number=1,
                text=doc102.raw_text,
                ocr_confidence=98.0,
                extraction_method='pymupdf_direct'
            )
            doc_fitz.close()

            ProcessingLog.objects.create(
                document=doc102,
                log_level=ProcessingLog.Level.INFO,
                stage='COMPLETED',
                message="Resume parsed successfully with 96% overall confidence."
            )
            self.stdout.write(self.style.SUCCESS("Created Document #102 (resume_elena_rostova.pdf)!"))

    def _create_invoice_001_pdf(self) -> bytes:
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)
        text = """ABC TECHNOLOGIES PVT LTD
Building 4, Cyber City, Phase III, Gurugram, India
contact@abctechnologies.com | +91 124 555 0192

TAX INVOICE

Invoice Number: INV-2026-001
Invoice Date: 15-11-2026
Vendor: ABC Technologies
Due Date: 30-11-2026

Billed To:
Zenith Solutions International
Floor 5, Innovation Hub, Bengaluru

Line Items:
1. Enterprise Cloud Computing Subscription (1 Month): ₹20,000
2. Managed Security & Threat Protection SLA: ₹5,000

Subtotal: ₹25,000
Total Amount: ₹25,000

Confidence scores will be estimates based on extraction rules and validation.
Thank you for your business!"""
        rect = fitz.Rect(50, 50, 545, 792)
        page.insert_textbox(rect, text, fontsize=11, fontname="helv")
        b = doc.tobytes()
        doc.close()
        return b

    def _create_resume_pdf(self) -> bytes:
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)
        text = """Elena Rostova
Senior AI & Machine Learning Engineer
elena.rostova.ml@gmail.com | (206) 555-8392 | Seattle, WA

PROFESSIONAL SUMMARY
Machine Learning Engineer with 7+ years developing scalable OCR pipelines.

EDUCATION
Master of Science in Computer Science, Stanford University (2019)
Bachelor of Science in Software Engineering, University of Washington (2017)

SKILLS & TECHNOLOGIES
Python, PyTorch, React, Django REST Framework, Tesseract OCR, PyMuPDF, Celery."""
        rect = fitz.Rect(50, 50, 545, 792)
        page.insert_textbox(rect, text, fontsize=11, fontname="helv")
        b = doc.tobytes()
        doc.close()
        return b
