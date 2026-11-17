import re
from typing import Dict, Any, Tuple

class DocumentClassifier:
    """
    Intelligent document classification engine using multi-feature pattern recognition,
    keyword distribution, and structural indicators.
    """

    CATEGORIES = {
        'invoice': {
            'label': 'Invoice',
            'keywords': [
                'invoice', 'bill to', 'ship to', 'invoice date', 'due date', 'subtotal',
                'balance due', 'tax rate', 'vat', 'gst', 'po box', 'remit to', 'amount due',
                'unit price', 'quantity', 'qty', 'line item', 'payment terms', 'net 30', 'invoice #'
            ],
            'regex': [
                r'invoice\s*(?:no\.?|number|#)?[:\s]*[A-Z0-9\-_]+',
                r'amount\s*due[:\s]*[\$€£₹]?\s*[0-9,.]+',
                r'total\s*(?:due|amount)?[:\s]*[\$€£₹]?\s*[0-9,.]+',
            ],
            'weight': 1.2
        },
        'receipt': {
            'label': 'Receipt',
            'keywords': [
                'receipt', 'cashier', 'register', 'subtotal', 'sales tax', 'tax', 'tip',
                'change due', 'cash', 'credit card', 'visa', 'mastercard', 'amex',
                'store #', 'merchant', 'terminal', 'thank you for your business',
                'total purchase', 'order #'
            ],
            'regex': [
                r'receipt\s*(?:no\.?|#)?[:\s]*[0-9A-Z]+',
                r'subtotal[:\s]*[\$€£₹]?\s*[0-9,.]+',
                r'cashier[:\s]*[a-zA-Z0-9]+',
            ],
            'weight': 1.1
        },
        'resume': {
            'label': 'Resume / CV',
            'keywords': [
                'resume', 'curriculum vitae', 'cv', 'experience', 'education', 'skills',
                'work experience', 'professional summary', 'employment history',
                'bachelor', 'master', 'university', 'college', 'gpa', 'certifications',
                'technologies', 'projects', 'github', 'linkedin', 'phone', 'email'
            ],
            'regex': [
                r'(?:curriculum\s+vitae|resume)',
                r'(?:work\s+)?experience\b',
                r'education\b',
                r'skills\b',
            ],
            'weight': 1.3
        },
        'id_card': {
            'label': 'ID Document',
            'keywords': [
                'passport', 'driver license', 'driving licence', 'identity card', 'national id',
                'identification', 'date of birth', 'dob', 'expiry date', 'date of expiry',
                'sex', 'gender', 'nationality', 'place of birth', 'issuing authority',
                'card number', 'dl no', 'license no', 'ssn', 'republic', 'department of motor'
            ],
            'regex': [
                r'(?:dob|date\s+of\s+birth)[:\s]*\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}',
                r'passport\s*(?:no\.?|number)?[:\s]*[A-Z0-9]+',
                r'licen[cs]e\s*(?:no\.?|number)?[:\s]*[A-Z0-9]+',
            ],
            'weight': 1.3
        },
        'contract': {
            'label': 'Contract / Agreement',
            'keywords': [
                'agreement', 'contract', 'parties', 'hereby', 'terms and conditions',
                'whereas', 'in witness whereof', 'governing law', 'confidentiality',
                'indemnification', 'termination', 'non-disclosure', 'effective date',
                'signatures', 'severability', 'liability', 'covenant', 'breach'
            ],
            'regex': [
                r'(?:this\s+agreement|contract\s+is\s+entered)',
                r'in\s+witness\s+whereof',
                r'effective\s+date[:\s]*',
            ],
            'weight': 1.2
        },
        'certificate': {
            'label': 'Certificate',
            'keywords': [
                'certificate', 'certify', 'certifies that', 'has successfully completed',
                'diploma', 'awarded to', 'completion of', 'degree of', 'honors',
                'accreditation', 'fulfillment of requirements', 'issued on', 'director'
            ],
            'regex': [
                r'this\s+is\s+to\s+certify\s+that',
                r'certificate\s+of\s+(?:completion|achievement|appreciation)',
                r'has\s+successfully\s+completed',
            ],
            'weight': 1.25
        },
        'form': {
            'label': 'Form',
            'keywords': [
                'form', 'application form', 'questionnaire', 'applicant', 'signature of applicant',
                'declaration', 'checkbox', 'official use only', 'part i', 'section a',
                'fill in block letters', 'tax return', 'w-2', '1099', 'w-9', 'registration form'
            ],
            'regex': [
                r'form\s+(?:[A-Z0-9\-]+)',
                r'for\s+official\s+use\s+only',
                r'application\s+form',
            ],
            'weight': 1.1
        },
        'report': {
            'label': 'Report',
            'keywords': [
                'report', 'annual report', 'executive summary', 'analysis', 'findings',
                'quarterly', 'financial statement', 'balance sheet', 'profit and loss',
                'methodology', 'conclusion', 'overview', 'performance'
            ],
            'regex': [
                r'(?:annual|quarterly|financial)\s+report',
                r'executive\s+summary',
                r'table\s+of\s+contents',
            ],
            'weight': 1.05
        }
    }

    @classmethod
    def classify(cls, text: str) -> Dict[str, Any]:
        """
        Classifies the document text into one of the known categories.
        Returns predicted category, confidence score, and candidate breakdown.
        """
        if not text or len(text.strip()) < 10:
            return {
                'category': 'other',
                'confidence': 30.0,
                'explanation': {'reason': 'Insufficient text content to reliably classify'}
            }

        text_lower = text.lower()
        # Look at the first 1500 chars (headers / introductory metadata) with higher importance
        header_text = text_lower[:1500]

        scores = {}
        matched_indicators = {}

        for cat, config in cls.CATEGORIES.items():
            cat_score = 0.0
            hits = []

            # 1. Keyword matching
            for kw in config['keywords']:
                # Extra weight if keyword is found in the document header
                if kw in header_text:
                    cat_score += 3.0
                    hits.append(f"header:{kw}")
                elif kw in text_lower:
                    cat_score += 1.0
                    hits.append(kw)

            # 2. Regex pattern matching
            for pattern in config.get('regex', []):
                if re.search(pattern, text_lower):
                    cat_score += 5.0
                    hits.append(f"regex_match")

            # Apply category-specific weight
            weighted_score = cat_score * config.get('weight', 1.0)
            scores[cat] = round(weighted_score, 2)
            matched_indicators[cat] = hits[:6] # keep top 6 clues

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_cat, top_score = sorted_scores[0]
        second_cat, second_score = sorted_scores[1] if len(sorted_scores) > 1 else (None, 0)

        # Confidence calculation
        # If score is very low, classify as 'other'
        if top_score < 4.0:
            predicted_cat = 'other'
            confidence = 50.0
        else:
            predicted_cat = top_cat
            # Margin between top and second score increases confidence
            margin = top_score - second_score
            base_conf = min(96.0, 65.0 + (top_score * 1.5))
            confidence = min(98.5, max(60.0, base_conf + min(15.0, margin * 2.0)))

        return {
            'category': predicted_cat,
            'confidence': round(confidence, 1),
            'top_score': top_score,
            'scores': scores,
            'explanation': {
                'clues': matched_indicators.get(top_cat, []),
                'margin': round(top_score - second_score, 2),
                'runner_up': second_cat
            }
        }

