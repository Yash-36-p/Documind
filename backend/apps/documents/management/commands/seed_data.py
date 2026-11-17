import os
import io
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
import pymupdf as fitz
from PIL import Image, ImageDraw, ImageFont

from apps.documents.models import Document
from apps.documents.tasks import run_document_processing

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds initial users and sample documents with OCR extraction for DocuMind'

    def handle(self, *args, **options):
        self.stdout.write("Seeding DocuMind demo users...")

        # 1. Admin user
        admin_user, created = User.objects.get_or_create(
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
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created admin user: admin / admin123"))

        # 2. Reviewer user
        reviewer_user, created = User.objects.get_or_create(
            username='reviewer',
            defaults={
                'email': 'reviewer@documind.ai',
                'first_name': 'Alex',
                'last_name': 'Rivera',
                'role': User.Role.REVIEWER,
                'organization': 'Apex Financial Audit'
            }
        )
        if created:
            reviewer_user.set_password('reviewer123')
            reviewer_user.save()
            self.stdout.write(self.style.SUCCESS("Created reviewer user: reviewer / reviewer123"))

        # 3. Viewer user
        viewer_user, created = User.objects.get_or_create(
            username='viewer',
            defaults={
                'email': 'viewer@documind.ai',
                'first_name': 'Taylor',
                'last_name': 'Brooks',
                'role': User.Role.VIEWER,
                'organization': 'Compliance Partners'
            }
        )
        if created:
            viewer_user.set_password('viewer123')
            viewer_user.save()
            self.stdout.write(self.style.SUCCESS("Created viewer user: viewer / viewer123"))

        # 4. Generate and seed sample documents if none exist
        if Document.objects.count() == 0:
            self.stdout.write("Generating sample documents...")

            # Document 1: Invoice PDF
            inv_pdf_bytes = self._create_sample_invoice_pdf()
            doc1 = Document.objects.create(
                title='Acme Corp Cloud Services Invoice',
                file_type='pdf',
                mime_type='application/pdf',
                uploaded_by=reviewer_user,
            )
            doc1.file.save('invoice_acme_2026.pdf', ContentFile(inv_pdf_bytes))
            doc1.file_size = len(inv_pdf_bytes)
            doc1.save()
            self.stdout.write("Processing sample Invoice PDF...")
            run_document_processing(str(doc1.id))

            # Document 2: Resume PDF
            resume_pdf_bytes = self._create_sample_resume_pdf()
            doc2 = Document.objects.create(
                title='Elena Rostova Senior AI Engineer Resume',
                file_type='pdf',
                mime_type='application/pdf',
                uploaded_by=reviewer_user,
            )
            doc2.file.save('resume_elena_rostova.pdf', ContentFile(resume_pdf_bytes))
            doc2.file_size = len(resume_pdf_bytes)
            doc2.save()
            self.stdout.write("Processing sample Resume PDF...")
            run_document_processing(str(doc2.id))

            # Document 3: ID Document image
            id_img_bytes = self._create_sample_id_image()
            doc3 = Document.objects.create(
                title='National Identity Card Scan',
                file_type='image',
                mime_type='image/png',
                uploaded_by=admin_user,
            )
            doc3.file.save('national_id_card.png', ContentFile(id_img_bytes))
            doc3.file_size = len(id_img_bytes)
            doc3.save()
            self.stdout.write("Processing sample ID Card image...")
            run_document_processing(str(doc3.id))

            self.stdout.write(self.style.SUCCESS("All sample documents generated and processed!"))
        else:
            self.stdout.write("Sample documents already exist.")

    def _create_sample_invoice_pdf(self) -> bytes:
        doc = fitz.open()
        page = doc.new_page(width=595, height=842) # A4

        text = """ACME CLOUD SOLUTIONS LLC
100 Innovation Way, Suite 400
San Francisco, CA 94107
contact@acmecloud.com | (415) 555-0199

INVOICE

Invoice Number: INV-2026-8842
Invoice Date: October 14, 2026
Payment Due Date: November 15, 2026

BILL TO:
Global Logistics Enterprises
Attn: Marcus Vance
450 Harbor Boulevard, Floor 12
Seattle, WA 98101
marcus.vance@globallogistics.com

--------------------------------------------------------------------------------
Description                           Qty      Unit Price        Total
--------------------------------------------------------------------------------
Enterprise Kubernetes Cluster         1        $ 3,200.00        $ 3,200.00
Dedicated GPU Compute (A100)          2        $ 1,850.00        $ 3,700.00
Cloud Object Storage (50 TB)          1        $   650.00        $   650.00
24/7 Premium SLA Support              1        $   950.00        $   950.00
--------------------------------------------------------------------------------

Subtotal: $ 8,500.00
Tax Rate (8.5%): $ 722.50
Total Amount Due: $ 9,222.50

Payment Terms: Net 30. Please remit to Wire Transfer AC #882910482.
Thank you for your business!
"""
        rect = fitz.Rect(50, 50, 545, 792)
        page.insert_textbox(rect, text, fontsize=11, fontname="helv")
        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes

    def _create_sample_resume_pdf(self) -> bytes:
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)

        text = """Elena Rostova
Senior AI & Machine Learning Engineer
elena.rostova.ml@gmail.com | (206) 555-8392 | Seattle, WA | github.com/erostova

PROFESSIONAL SUMMARY
Experienced Machine Learning Engineer with 7+ years developing scalable computer vision,
natural language processing, and automated OCR pipelines for enterprise document processing.

EDUCATION
Master of Science in Computer Science, Stanford University (2019)
Bachelor of Science in Software Engineering, University of Washington (2017)

TECHNICAL SKILLS & TECHNOLOGIES
Languages & Frameworks: Python, PyTorch, TensorFlow, React, FastAPI, Django REST Framework
Computer Vision & NLP: PyMuPDF, Tesseract OCR, OpenCV, HuggingFace Transformers, SpaCy
Infrastructure: Docker, Kubernetes, Celery, Redis, PostgreSQL, AWS SageMaker

WORK EXPERIENCE
Staff AI Engineer - CogniFlow Technologies (2022 - Present)
- Architected end-to-end intelligent document processing pipeline processing 2M+ docs daily.
- Improved invoice table extraction accuracy from 84% to 97.4% using hybrid deep learning.
- Reduced OCR processing latency by 45% utilizing asynchronous Celery queues.

Senior Machine Learning Engineer - DataNova Systems (2019 - 2022)
- Built automated resume parsing and key-entity extraction models for HR tech platform.
- Spearheaded document classification engine achieving 98.2% macro F1 score.
"""
        rect = fitz.Rect(50, 50, 545, 792)
        page.insert_textbox(rect, text, fontsize=11, fontname="helv")
        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes

    def _create_sample_id_image(self) -> bytes:
        img = Image.new('RGB', (800, 500), color=(240, 244, 248))
        draw = ImageDraw.Draw(img)

        # Header bar
        draw.rectangle([0, 0, 800, 70], fill=(30, 41, 59))
        draw.text((30, 22), "REPUBLIC OF TECHLAND - NATIONAL IDENTIFICATION CARD", fill=(255, 255, 255))

        # Photo placeholder
        draw.rectangle([40, 100, 220, 340], fill=(203, 213, 225), outline=(100, 116, 139), width=2)
        draw.text((80, 210), "[PHOTO]", fill=(71, 85, 105))

        # ID Details
        details = [
            ("Document ID Number:", "TL-8392-49102-X"),
            ("Full Name:", "David Alexander Kim"),
            ("Date of Birth (DOB):", "14/08/1992"),
            ("Sex / Gender:", "M"),
            ("Nationality:", "Techlandian"),
            ("Issuing Authority:", "Department of Civil Registry"),
            ("Date of Issue:", "12/01/2021"),
            ("Expiration Date:", "12/01/2031"),
        ]

        y_offset = 100
        for label, val in details:
            draw.text((250, y_offset), f"{label}  {val}", fill=(15, 23, 42))
            y_offset += 32

        # Barcode strip simulation
        draw.rectangle([40, 420, 760, 460], fill=(51, 65, 85))

        out_io = io.BytesIO()
        img.save(out_io, format='PNG')
        return out_io.getvalue()
