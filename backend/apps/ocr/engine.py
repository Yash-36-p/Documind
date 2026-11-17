import os
import io
import time
import logging
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from pytesseract import Output
import pymupdf as fitz
from django.conf import settings
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

class OcrEngine:
    """
    Intelligent OCR Engine supporting hybrid extraction:
    - Direct digital text extraction via PyMuPDF for digital PDFs
    - Rasterization & Tesseract OCR for scanned PDF pages
    - Tesseract OCR + Pillow image preprocessing for PNG, JPG, JPEG
    - First page thumbnail generation for visual preview
    """

    @classmethod
    def process_file(cls, file_path, file_type='pdf'):
        start_time = time.time()
        file_type = file_type.lower().replace('.', '')
        # If file_type is generic 'image', inspect file extension from file_path
        ext = os.path.splitext(file_path)[1].lower().replace('.', '')

        if file_type == 'pdf' or ext == 'pdf':
            result = cls._process_pdf(file_path)
        elif file_type in ['png', 'jpg', 'jpeg', 'webp', 'tiff', 'bmp', 'image'] or ext in ['png', 'jpg', 'jpeg', 'webp', 'tiff', 'bmp']:
            result = cls._process_image(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type} (ext: {ext})")

        elapsed_ms = int((time.time() - start_time) * 1000)
        result['elapsed_ms'] = elapsed_ms
        return result

    @classmethod
    def _process_pdf(cls, file_path):
        doc = fitz.open(file_path)
        page_count = len(doc)
        pages_data = []
        total_confidence = 0.0
        full_text_parts = []
        first_page_thumb_bytes = None

        for page_idx in range(page_count):
            page_num = page_idx + 1
            page = doc[page_idx]

            # 1. Try digital text extraction first
            direct_text = page.get_text().strip()
            
            # Generate high-res image of page for preview and potential OCR
            pix = page.get_pixmap(dpi=150)
            img_bytes = pix.tobytes("png")
            pil_img = Image.open(io.BytesIO(img_bytes))

            if page_idx == 0:
                # Save thumbnail for document preview
                thumb = pil_img.copy()
                thumb.thumbnail((600, 800), Image.Resampling.LANCZOS)
                thumb_io = io.BytesIO()
                thumb.save(thumb_io, format='JPEG', quality=85)
                first_page_thumb_bytes = thumb_io.getvalue()

            # Determine if page is digital or scanned
            # If direct text has >= 40 characters and multiple words, treat as digital
            is_digital = len(direct_text) >= 40 and len(direct_text.split()) >= 8

            if is_digital:
                text = direct_text
                # PyMuPDF digital extraction is very accurate (~98%)
                confidence = 98.0
                method = 'pymupdf_direct'
            else:
                # Scanned or image-based PDF page: use Tesseract OCR
                text, confidence = cls._ocr_image_pil(pil_img)
                method = 'tesseract_ocr'
                if not text and direct_text:
                    text = direct_text
                    confidence = 85.0

            # Generate page thumbnail
            page_thumb_io = io.BytesIO()
            page_thumb = pil_img.copy()
            page_thumb.thumbnail((400, 550), Image.Resampling.LANCZOS)
            page_thumb.save(page_thumb_io, format='JPEG', quality=80)

            pages_data.append({
                'page_number': page_num,
                'text': text,
                'ocr_confidence': round(confidence, 2),
                'extraction_method': method,
                'thumbnail_bytes': page_thumb_io.getvalue(),
                'char_count': len(text),
                'word_count': len(text.split()),
            })

            full_text_parts.append(text)
            total_confidence += confidence

        doc.close()

        avg_confidence = round(total_confidence / max(1, page_count), 2)
        full_text = "\n\n--- Page Break ---\n\n".join(full_text_parts)

        return {
            'page_count': page_count,
            'full_text': full_text,
            'overall_confidence': avg_confidence,
            'pages': pages_data,
            'first_page_thumb_bytes': first_page_thumb_bytes,
            'file_type': 'pdf'
        }

    @classmethod
    def _process_image(cls, file_path):
        with Image.open(file_path) as original_img:
            # Convert to RGB if needed
            if original_img.mode not in ('RGB', 'L'):
                img = original_img.convert('RGB')
            else:
                img = original_img.copy()

            # Generate preview thumbnail
            thumb = img.copy()
            thumb.thumbnail((600, 800), Image.Resampling.LANCZOS)
            thumb_io = io.BytesIO()
            thumb.save(thumb_io, format='JPEG', quality=85)
            first_page_thumb_bytes = thumb_io.getvalue()

            # Preprocess image for OCR optimization
            ocr_text, confidence = cls._ocr_image_pil(img)

            pages_data = [{
                'page_number': 1,
                'text': ocr_text,
                'ocr_confidence': round(confidence, 2),
                'extraction_method': 'tesseract_ocr',
                'thumbnail_bytes': first_page_thumb_bytes,
                'char_count': len(ocr_text),
                'word_count': len(ocr_text.split()),
            }]

            return {
                'page_count': 1,
                'full_text': ocr_text,
                'overall_confidence': round(confidence, 2),
                'pages': pages_data,
                'first_page_thumb_bytes': first_page_thumb_bytes,
                'file_type': 'image'
            }

    @classmethod
    def _ocr_image_pil(cls, pil_img):
        """
        Enhance image using Pillow and extract text and confidence using Tesseract.
        """
        # Pillow pre-processing
        # Convert to grayscale
        gray = pil_img.convert('L')
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(gray)
        enhanced = enhancer.enhance(1.8)
        # Slight sharpening
        sharpened = enhanced.filter(ImageFilter.SHARPEN)

        try:
            # Run pytesseract with data output for confidence calculation
            data = pytesseract.image_to_data(sharpened, output_type=Output.DICT)
            n_boxes = len(data['text'])
            confidences = []
            words = []

            for i in range(n_boxes):
                text_word = data['text'][i].strip()
                conf = float(data['conf'][i])
                if text_word and conf > 0:
                    confidences.append(conf)
                    words.append(text_word)

            extracted_text = pytesseract.image_to_string(sharpened).strip()
            
            if confidences:
                avg_conf = sum(confidences) / len(confidences)
            else:
                avg_conf = 70.0 if extracted_text else 0.0

            return extracted_text, avg_conf

        except Exception as e:
            logger.warning(f"Tesseract OCR fallback encountered error: {e}")
            try:
                # Direct string fallback
                text = pytesseract.image_to_string(pil_img).strip()
                return text, 75.0 if text else 0.0
            except Exception as ex:
                logger.error(f"Tesseract completely failed: {ex}")
                return "", 0.0

