"""
DocumentSummarizer — Rule-based, offline NLP summarizer for DocuMind.

Generates a 3-6 sentence human-readable summary and a list of key points
from extracted fields + raw OCR text, tailored per document type.
No external APIs. Zero cost.
"""
import re
import textwrap
from typing import List, Dict, Any


class DocumentSummarizer:
    """
    Generates summaries from extracted fields and raw text.
    Entirely rule-based — works offline, no paid services required.
    """

    # -----------------------------------------------------------------
    # Public entry point
    # -----------------------------------------------------------------
    @classmethod
    def summarize(
        cls,
        document_type: str,
        raw_text: str,
        extracted_fields: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Returns:
            {
              "summary":    str,          # 3-6 sentence paragraph
              "key_points": List[str],    # 3-5 bullet strings
              "word_count": int,          # word count of raw_text
            }
        """
        fields = cls._normalise_fields(extracted_fields)
        word_count = len(raw_text.split()) if raw_text else 0
        doc_type_lower = (document_type or '').lower()

        # Pick the right handler
        if 'invoice' in doc_type_lower:
            summary, key_points = cls._invoice(fields, raw_text)
        elif 'receipt' in doc_type_lower:
            summary, key_points = cls._receipt(fields, raw_text)
        elif 'resume' in doc_type_lower or 'cv' in doc_type_lower:
            summary, key_points = cls._resume(fields, raw_text)
        elif 'id' in doc_type_lower:
            summary, key_points = cls._id_document(fields, raw_text)
        elif 'contract' in doc_type_lower:
            summary, key_points = cls._contract(fields, raw_text)
        elif 'certificate' in doc_type_lower:
            summary, key_points = cls._certificate(fields, raw_text)
        elif 'form' in doc_type_lower:
            summary, key_points = cls._form(fields, raw_text)
        elif 'report' in doc_type_lower:
            summary, key_points = cls._report(fields, raw_text)
        else:
            summary, key_points = cls._generic(fields, raw_text, document_type)

        # Fallback if summary is still empty
        if not summary:
            summary, key_points = cls._generic(fields, raw_text, document_type)

        return {
            "summary": summary.strip(),
            "key_points": key_points[:5],
            "word_count": word_count,
        }

    # -----------------------------------------------------------------
    # Field normaliser — unify field dict shapes from extractor
    # -----------------------------------------------------------------
    @staticmethod
    def _normalise_fields(extracted_fields: List[Dict]) -> Dict[str, str]:
        """
        Returns a flat {key: value} dict, lowercased keys, stripped values.
        Accepts both {'field_key':…,'field_value':…} and {'field_label':…,'extracted_value':…} shapes.
        """
        result = {}
        for ef in (extracted_fields or []):
            key = (
                ef.get('field_key') or
                ef.get('field_name') or
                ef.get('field_label', '')
            ).lower().replace(' ', '_').replace('-', '_')
            val = str(
                ef.get('field_value') or
                ef.get('extracted_value') or ''
            ).strip()
            if key and val:
                result[key] = val
        return result

    # -----------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------
    @staticmethod
    def _get(fields: Dict, *keys: str, default: str = '') -> str:
        """Try multiple keys; return first non-empty value."""
        for k in keys:
            v = fields.get(k, '')
            if v:
                return v
        return default

    @staticmethod
    def _sentences_from_text(text: str, n: int = 3) -> str:
        """Extract first n meaningful sentences from raw text."""
        if not text:
            return ''
        # Split by sentence-ending punctuation
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        # Keep only sentences with ≥ 4 words
        clean = [s.strip() for s in sentences if len(s.split()) >= 4]
        return ' '.join(clean[:n])

    # -----------------------------------------------------------------
    # Type-specific summarisers
    # -----------------------------------------------------------------
    @classmethod
    def _invoice(cls, f: Dict, raw: str):
        g = cls._get
        vendor   = g(f, 'vendor_name', 'vendor', 'company', 'issuer', 'billed_from', 'seller')
        inv_no   = g(f, 'invoice_number', 'invoice_no', 'inv_number', 'invoice_id', 'reference_number')
        date     = g(f, 'invoice_date', 'date', 'issue_date', 'billing_date')
        due      = g(f, 'due_date', 'payment_due', 'payment_due_date')
        total    = g(f, 'total_amount', 'grand_total', 'amount_due', 'total', 'amount', 'invoice_total')
        tax      = g(f, 'tax_amount', 'gst', 'vat', 'tax', 'cgst', 'sgst', 'igst')
        client   = g(f, 'client_name', 'billed_to', 'customer', 'recipient', 'buyer')
        currency = g(f, 'currency', default='')

        parts = []
        # Sentence 1 — what it is
        s1 = "This is a financial invoice"
        if vendor:
            s1 += f" issued by {vendor}"
        if client:
            s1 += f" to {client}"
        if date:
            s1 += f" dated {date}"
        parts.append(s1 + ".")

        # Sentence 2 — amounts
        if total or inv_no:
            s2 = ""
            if inv_no:
                s2 += f"Invoice number {inv_no}"
            if total:
                amt = f"{currency} {total}".strip() if currency else total
                connector = " with a total amount of " if inv_no else "The total amount due is "
                s2 += connector + amt
            parts.append(s2.strip().rstrip(',') + ".")

        # Sentence 3 — tax & due date
        extras = []
        if tax:
            extras.append(f"Tax: {tax}")
        if due:
            extras.append(f"payment due by {due}")
        if extras:
            parts.append("Additional details — " + "; ".join(extras) + ".")

        # Sentence 4 — fallback from raw text if few fields
        if len(parts) < 2:
            snippet = cls._sentences_from_text(raw, 2)
            if snippet:
                parts.append(snippet)

        summary = " ".join(parts)

        # Key points
        kp = []
        if vendor:   kp.append(f"Vendor / Issuer: {vendor}")
        if inv_no:   kp.append(f"Invoice #: {inv_no}")
        if date:     kp.append(f"Invoice Date: {date}")
        if total:    kp.append(f"Total Amount: {(currency+' ').lstrip()}{total}")
        if due:      kp.append(f"Payment Due: {due}")
        if tax:      kp.append(f"Tax Charged: {tax}")
        if client:   kp.append(f"Billed To: {client}")

        return summary, kp

    @classmethod
    def _receipt(cls, f: Dict, raw: str):
        g = cls._get
        merchant = g(f, 'merchant_name', 'merchant', 'store', 'vendor', 'seller')
        date     = g(f, 'date', 'transaction_date', 'purchase_date', 'receipt_date')
        total    = g(f, 'total_amount', 'total', 'amount', 'grand_total')
        payment  = g(f, 'payment_method', 'payment_mode', 'paid_via')
        receipt  = g(f, 'receipt_number', 'transaction_id', 'reference')
        tax      = g(f, 'tax', 'tax_amount', 'vat', 'gst')

        parts = []
        s1 = "This is a purchase receipt"
        if merchant:
            s1 += f" from {merchant}"
        if date:
            s1 += f" dated {date}"
        parts.append(s1 + ".")

        if total:
            s2 = f"The total purchase amount was {total}"
            if payment:
                s2 += f" paid via {payment}"
            parts.append(s2 + ".")

        if receipt:
            parts.append(f"Receipt / transaction reference: {receipt}.")
        if tax:
            parts.append(f"Tax applied: {tax}.")

        if len(parts) < 2:
            parts.append(cls._sentences_from_text(raw, 2))

        kp = []
        if merchant: kp.append(f"Merchant: {merchant}")
        if date:     kp.append(f"Date: {date}")
        if total:    kp.append(f"Total: {total}")
        if payment:  kp.append(f"Payment Method: {payment}")
        if receipt:  kp.append(f"Transaction Ref: {receipt}")
        if tax:      kp.append(f"Tax: {tax}")

        return " ".join(parts), kp

    @classmethod
    def _resume(cls, f: Dict, raw: str):
        g = cls._get
        name   = g(f, 'full_name', 'name', 'candidate_name', 'applicant_name')
        email  = g(f, 'email', 'email_address', 'contact_email')
        phone  = g(f, 'phone', 'mobile', 'phone_number', 'contact_number')
        title  = g(f, 'job_title', 'current_title', 'designation', 'position', 'role')
        skills = g(f, 'skills', 'key_skills', 'technical_skills', 'expertise')
        edu    = g(f, 'education', 'degree', 'qualification', 'highest_degree')
        exp    = g(f, 'experience', 'years_of_experience', 'total_experience', 'work_experience')
        company= g(f, 'current_company', 'employer', 'organization', 'current_employer')

        parts = []
        s1 = "This document is a professional résumé"
        if name:
            s1 += f" for {name}"
        if title:
            s1 += f", currently working as {title}"
        if company:
            s1 += f" at {company}"
        parts.append(s1 + ".")

        if skills:
            parts.append(f"Key skills and expertise include: {skills}.")
        if edu:
            parts.append(f"Educational background: {edu}.")
        if exp:
            parts.append(f"Total work experience: {exp}.")

        contact_parts = []
        if email:   contact_parts.append(email)
        if phone:   contact_parts.append(phone)
        if contact_parts:
            parts.append(f"Contact: {', '.join(contact_parts)}.")

        if len(parts) < 2:
            parts.append(cls._sentences_from_text(raw, 2))

        kp = []
        if name:    kp.append(f"Candidate: {name}")
        if title:   kp.append(f"Role: {title}")
        if skills:  kp.append(f"Skills: {skills[:80]}")
        if edu:     kp.append(f"Education: {edu}")
        if exp:     kp.append(f"Experience: {exp}")
        if email:   kp.append(f"Email: {email}")

        return " ".join(parts), kp

    @classmethod
    def _id_document(cls, f: Dict, raw: str):
        g = cls._get
        name    = g(f, 'full_name', 'name', 'holder_name', 'cardholder_name')
        dob     = g(f, 'date_of_birth', 'dob', 'birth_date')
        expiry  = g(f, 'expiry_date', 'expiration_date', 'valid_until', 'valid_through')
        id_no   = g(f, 'id_number', 'document_number', 'card_number', 'passport_number', 'license_number')
        country = g(f, 'country', 'nationality', 'issuing_country')
        issued  = g(f, 'issue_date', 'date_of_issue', 'issued_on')
        gender  = g(f, 'gender', 'sex')
        address = g(f, 'address', 'permanent_address', 'residential_address')

        parts = []
        s1 = "This is an official identity document"
        if name:
            s1 += f" belonging to {name}"
        if country:
            s1 += f" ({country})"
        parts.append(s1 + ".")

        if id_no:
            parts.append(f"Document number: {id_no}.")
        if dob or gender:
            bio = []
            if dob: bio.append(f"DOB: {dob}")
            if gender: bio.append(f"Gender: {gender}")
            parts.append("; ".join(bio) + ".")
        if issued or expiry:
            validity = []
            if issued: validity.append(f"issued {issued}")
            if expiry: validity.append(f"valid until {expiry}")
            parts.append("Document validity — " + ", ".join(validity) + ".")
        if address:
            parts.append(f"Registered address: {address[:100]}.")

        if len(parts) < 2:
            parts.append(cls._sentences_from_text(raw, 2))

        kp = []
        if name:    kp.append(f"ID Holder: {name}")
        if id_no:   kp.append(f"Document #: {id_no}")
        if dob:     kp.append(f"Date of Birth: {dob}")
        if expiry:  kp.append(f"Expiry: {expiry}")
        if country: kp.append(f"Country: {country}")
        if gender:  kp.append(f"Gender: {gender}")

        return " ".join(parts), kp

    @classmethod
    def _contract(cls, f: Dict, raw: str):
        g = cls._get
        date      = g(f, 'date', 'contract_date', 'agreement_date', 'effective_date', 'signing_date')
        party1    = g(f, 'party_1', 'first_party', 'employer', 'client', 'company')
        party2    = g(f, 'party_2', 'second_party', 'employee', 'contractor', 'vendor')
        amount    = g(f, 'contract_value', 'total_value', 'amount', 'compensation', 'salary')
        duration  = g(f, 'duration', 'contract_period', 'term', 'validity_period')
        subject   = g(f, 'subject', 'purpose', 'contract_type', 'agreement_type')

        parts = []
        s1 = "This is a legal contract or agreement"
        if subject:
            s1 += f" of type: {subject}"
        if date:
            s1 += f", dated {date}"
        parts.append(s1 + ".")

        if party1 or party2:
            parties = " and ".join(filter(None, [party1, party2]))
            parts.append(f"The agreement is between: {parties}.")
        if amount:
            parts.append(f"Contract value / compensation: {amount}.")
        if duration:
            parts.append(f"Duration / term: {duration}.")

        # Pull first meaningful sentences from raw text as context
        snippet = cls._sentences_from_text(raw, 2)
        if snippet and len(parts) < 3:
            parts.append(snippet)

        kp = []
        if date:     kp.append(f"Date: {date}")
        if party1:   kp.append(f"Party 1: {party1}")
        if party2:   kp.append(f"Party 2: {party2}")
        if amount:   kp.append(f"Value: {amount}")
        if duration: kp.append(f"Term: {duration}")
        if subject:  kp.append(f"Type: {subject}")

        return " ".join(parts), kp

    @classmethod
    def _certificate(cls, f: Dict, raw: str):
        g = cls._get
        name    = g(f, 'recipient_name', 'full_name', 'name', 'awardee')
        cert    = g(f, 'certificate_title', 'course_name', 'program', 'award_title', 'certificate_type')
        issuer  = g(f, 'issuing_organization', 'issuer', 'organization', 'institution', 'authority')
        date    = g(f, 'date_issued', 'issue_date', 'award_date', 'completion_date', 'date')
        cert_no = g(f, 'certificate_number', 'cert_id', 'registration_number')

        parts = []
        s1 = "This is a certificate"
        if cert:
            s1 += f" for {cert}"
        if name:
            s1 += f", awarded to {name}"
        if issuer:
            s1 += f" by {issuer}"
        if date:
            s1 += f" on {date}"
        parts.append(s1 + ".")

        if cert_no:
            parts.append(f"Certificate number: {cert_no}.")

        if len(parts) < 2:
            parts.append(cls._sentences_from_text(raw, 2))

        kp = []
        if name:    kp.append(f"Recipient: {name}")
        if cert:    kp.append(f"Certificate: {cert}")
        if issuer:  kp.append(f"Issued by: {issuer}")
        if date:    kp.append(f"Date: {date}")
        if cert_no: kp.append(f"Cert #: {cert_no}")

        return " ".join(parts), kp

    @classmethod
    def _form(cls, f: Dict, raw: str):
        g = cls._get
        form_name = g(f, 'form_title', 'form_name', 'form_type', 'subject')
        submitter = g(f, 'full_name', 'name', 'applicant', 'submitted_by', 'respondent')
        date      = g(f, 'date', 'submission_date', 'form_date')
        ref       = g(f, 'reference_number', 'form_number', 'application_number')

        parts = []
        s1 = "This is a form"
        if form_name:
            s1 += f" titled '{form_name}'"
        if submitter:
            s1 += f" submitted by {submitter}"
        if date:
            s1 += f" on {date}"
        parts.append(s1 + ".")

        if ref:
            parts.append(f"Reference / application number: {ref}.")

        # Summarise field values
        notable = [(k, v) for k, v in f.items() if k not in
                   ('form_title','form_name','form_type','full_name','name',
                    'date','reference_number','form_number')]
        if notable:
            field_str = "; ".join(f"{k.replace('_',' ').title()}: {v}" for k, v in notable[:4])
            parts.append(f"Key form data — {field_str}.")

        if len(parts) < 2:
            parts.append(cls._sentences_from_text(raw, 2))

        kp = []
        if form_name:  kp.append(f"Form: {form_name}")
        if submitter:  kp.append(f"Submitted By: {submitter}")
        if date:       kp.append(f"Date: {date}")
        if ref:        kp.append(f"Reference #: {ref}")
        for k, v in notable[:2]:
            kp.append(f"{k.replace('_',' ').title()}: {v}")

        return " ".join(parts), kp

    @classmethod
    def _report(cls, f: Dict, raw: str):
        g = cls._get
        title   = g(f, 'report_title', 'title', 'subject', 'report_name')
        author  = g(f, 'author', 'prepared_by', 'submitted_by', 'analyst')
        date    = g(f, 'date', 'report_date', 'prepared_on', 'submission_date')
        org     = g(f, 'organization', 'company', 'department', 'institution')
        period  = g(f, 'reporting_period', 'period', 'financial_year', 'quarter')

        parts = []
        s1 = "This is a report"
        if title:
            s1 += f" titled '{title}'"
        if author:
            s1 += f", prepared by {author}"
        if org:
            s1 += f" at {org}"
        if date:
            s1 += f" dated {date}"
        parts.append(s1 + ".")

        if period:
            parts.append(f"Reporting period: {period}.")

        snippet = cls._sentences_from_text(raw, 3)
        if snippet:
            parts.append(snippet)

        kp = []
        if title:   kp.append(f"Title: {title}")
        if author:  kp.append(f"Author: {author}")
        if org:     kp.append(f"Organization: {org}")
        if date:    kp.append(f"Date: {date}")
        if period:  kp.append(f"Period: {period}")

        return " ".join(parts), kp

    @classmethod
    def _generic(cls, f: Dict, raw: str, doc_type: str = 'Document'):
        """Fallback generic summariser — works for any document type."""
        type_label = doc_type or "Document"

        parts = [f"This document has been classified as a {type_label}."]

        # Summarise top extracted fields
        if f:
            field_items = list(f.items())[:5]
            field_str = "; ".join(
                f"{k.replace('_', ' ').title()}: {v}" for k, v in field_items
            )
            parts.append(f"Key extracted information — {field_str}.")

        # Pull sentences from raw text
        snippet = cls._sentences_from_text(raw, 3)
        if snippet:
            parts.append(snippet)

        if not f and not raw:
            parts.append("No text or structured data was extracted from this document.")

        kp = [
            f"{k.replace('_',' ').title()}: {v}"
            for k, v in list(f.items())[:5]
        ]

        return " ".join(parts), kp
