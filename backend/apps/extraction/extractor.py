import re
from datetime import datetime
from typing import List, Dict, Any

class InformationExtractor:
    """
    High-accuracy information extraction engine for documents.
    Extracts invoice numbers, dates, amounts, taxes, contacts, names,
    organizations, and document-specific key fields.
    """

    @classmethod
    def extract_fields(cls, text: str, category: str = 'other') -> List[Dict[str, Any]]:
        """
        Extracts structured fields from raw text with confidence scores,
        field types, and labels.
        """
        if not text:
            return []

        fields = []
        cleaned_text = text.replace('\r', '')
        lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]

        # 1. Invoice / Reference Number (skip for resumes)
        if category != 'resume':
            inv_field = cls._extract_invoice_number(cleaned_text, lines)
            if inv_field:
                fields.append(inv_field)

        # 2. Financial Amounts (Total, Subtotal, Tax)
        amount_fields = cls._extract_amounts(cleaned_text, lines)
        fields.extend(amount_fields)

        # 3. Dates (Document Date, Due Date, DOB)
        date_fields = cls._extract_dates(cleaned_text, lines, category)
        fields.extend(date_fields)

        # 4. Contacts (Emails, Phones, Websites)
        contact_fields = cls._extract_contacts(cleaned_text)
        fields.extend(contact_fields)

        # 5. Organization / Company / Vendor Name
        org_field = cls._extract_organization(lines, category)
        if org_field:
            fields.append(org_field)

        # 6. Person / Customer / Applicant Name
        person_field = cls._extract_person_name(lines, category)
        if person_field:
            fields.append(person_field)

        # 7. Category-specific extraction
        if category == 'resume':
            resume_fields = cls._extract_resume_fields(cleaned_text, lines)
            fields.extend(resume_fields)
        elif category == 'id_card':
            id_fields = cls._extract_id_fields(cleaned_text, lines)
            fields.extend(id_fields)

        return fields

    @classmethod
    def _extract_invoice_number(cls, text: str, lines: List[str]) -> Dict[str, Any]:
        patterns = [
            (r'invoice\s+(?:number|num|no\.?|#)[:\s]+([A-Z0-9\-_/]{3,30})', 98.0),
            (r'(?:bill|receipt|order)\s+(?:number|num|no\.?|#)[:\s]+([A-Z0-9\-_/]{3,30})', 95.0),
            (r'invoice\s*#[:\s]*([A-Z0-9\-_/]{3,30})', 95.0),
            (r'(?:reference|ref)\s+(?:number|no\.?|#)[:\s]+([A-Z0-9\-_/]{3,30})', 90.0),
            (r'invoice[:\s]+([A-Z0-9\-_]{4,30})', 85.0),
            (r'#\s*([0-9]{4,12})', 80.0),
        ]
        for pattern, base_conf in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                # Exclude purely common words
                if val.lower() not in ['date', 'amount', 'total', 'due', 'usd', 'eur', 'invoice', 'number', 'no', 'bill', 'acme']:
                    return {
                        'field_key': 'invoice_number',
                        'field_label': 'Invoice / Reference #',
                        'field_value': val,
                        'original_value': val,
                        'confidence': base_conf,
                        'field_type': 'id_number',
                        'context_snippet': match.group(0)
                    }
        return None

    @classmethod
    def _extract_amounts(cls, text: str, lines: List[str]) -> List[Dict[str, Any]]:
        extracted = []
        currency_symbol = '$'
        for sym in ['$', '€', '£', '₹', 'USD', 'EUR', 'GBP', 'INR']:
            if sym in text:
                currency_symbol = sym
                break

        # Patterns for Total Amount
        total_patterns = [
            (r'(?:total\s*amount|balance\s*due|amount\s*due|grand\s*total|total\s*usd|total\s*eur|total)[:\s]*[\$€£₹]?\s*([0-9]{1,3}(?:[,.][0-9]{3})*(?:\.[0-9]{2}))', 95.0),
            (r'(?:total\s*amount|balance\s*due|amount\s*due|grand\s*total|total)[:\s]*[\$€£₹]?\s*([0-9]+(?:\.[0-9]{2}))', 92.0),
            (r'(?:total)[:\s]*[\$€£₹]?\s*([0-9,.]+)', 82.0),
        ]

        total_found = False
        for pattern, conf in total_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                extracted.append({
                    'field_key': 'total_amount',
                    'field_label': f'Total Amount ({currency_symbol})',
                    'field_value': f"{currency_symbol} {val}" if not val.startswith(currency_symbol) else val,
                    'original_value': f"{currency_symbol} {val}",
                    'confidence': conf,
                    'field_type': 'currency',
                    'context_snippet': match.group(0)
                })
                total_found = True
                break

        # Patterns for Subtotal
        subtotal_match = re.search(r'(?:subtotal|sub-total|net\s*amount)[:\s]*[\$€£₹]?\s*([0-9,.]+)', text, re.IGNORECASE)
        if subtotal_match:
            val = subtotal_match.group(1).strip()
            extracted.append({
                'field_key': 'subtotal_amount',
                'field_label': f'Subtotal ({currency_symbol})',
                'field_value': f"{currency_symbol} {val}",
                'original_value': f"{currency_symbol} {val}",
                'confidence': 90.0,
                'field_type': 'currency',
                'context_snippet': subtotal_match.group(0)
            })

        # Patterns for Tax / VAT / GST
        tax_match = re.search(r'(?:tax|vat|gst|sales\s*tax)(?:\s*\(\d+%\))?[:\s]*[\$€£₹]?\s*([0-9,.]+)', text, re.IGNORECASE)
        if tax_match:
            val = tax_match.group(1).strip()
            extracted.append({
                'field_key': 'tax_amount',
                'field_label': f'Tax / VAT ({currency_symbol})',
                'field_value': f"{currency_symbol} {val}",
                'original_value': f"{currency_symbol} {val}",
                'confidence': 88.0,
                'field_type': 'currency',
                'context_snippet': tax_match.group(0)
            })

        return extracted

    @classmethod
    def _extract_dates(cls, text: str, lines: List[str], category: str) -> List[Dict[str, Any]]:
        dates = []
        # General date regex: DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD, Month DD, YYYY
        date_re = r'\b(?:\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{4}[\-\/]\d{1,2}[\-\/]\d{1,2}|(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+\d{4})\b'

        # Invoice Date / Issue Date
        issue_match = re.search(rf'(?:invoice\s*date|issue\s*date|date\s*of\s*issue|bill\s*date|date)[:\s]*({date_re})', text, re.IGNORECASE)
        if issue_match:
            val = issue_match.group(1).strip()
            dates.append({
                'field_key': 'issue_date',
                'field_label': 'Document Date',
                'field_value': val,
                'original_value': val,
                'confidence': 93.0,
                'field_type': 'date',
                'context_snippet': issue_match.group(0)
            })
        else:
            # Fallback search for any prominent date
            first_date = re.search(date_re, text)
            if first_date:
                val = first_date.group(0).strip()
                dates.append({
                    'field_key': 'document_date',
                    'field_label': 'Date',
                    'field_value': val,
                    'original_value': val,
                    'confidence': 80.0,
                    'field_type': 'date',
                    'context_snippet': val
                })

        # Due Date
        due_match = re.search(rf'(?:due\s*date|payment\s*due|pay\s*by)[:\s]*({date_re})', text, re.IGNORECASE)
        if due_match:
            val = due_match.group(1).strip()
            dates.append({
                'field_key': 'due_date',
                'field_label': 'Due Date',
                'field_value': val,
                'original_value': val,
                'confidence': 91.0,
                'field_type': 'date',
                'context_snippet': due_match.group(0)
            })

        return dates

    @classmethod
    def _extract_contacts(cls, text: str) -> List[Dict[str, Any]]:
        contacts = []

        # Emails
        email_matches = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
        if email_matches:
            email_val = email_matches[0]
            contacts.append({
                'field_key': 'email',
                'field_label': 'Email Address',
                'field_value': email_val,
                'original_value': email_val,
                'confidence': 96.0,
                'field_type': 'email',
                'context_snippet': email_val
            })

        # Phone numbers
        phone_matches = re.findall(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        if phone_matches:
            # Clean string
            valid_phones = [p.strip() for p in phone_matches if len(re.sub(r'\D', '', p)) >= 10]
            if valid_phones:
                phone_val = valid_phones[0]
                contacts.append({
                    'field_key': 'phone',
                    'field_label': 'Phone Number',
                    'field_value': phone_val,
                    'original_value': phone_val,
                    'confidence': 90.0,
                    'field_type': 'phone',
                    'context_snippet': phone_val
                })

        return contacts

    @classmethod
    def _extract_organization(cls, lines: List[str], category: str) -> Dict[str, Any]:
        """
        Often the vendor or company name is located within the first 5 lines.
        """
        if not lines:
            return None

        for line in lines[:5]:
            cleaned = line.strip()
            # Ignore lines that are strictly numbers, dates, or headers like "INVOICE"
            if len(cleaned) > 2 and len(cleaned) < 60:
                if not re.search(r'^(?:invoice|bill|receipt|resume|curriculum|page|\d+|date|total)', cleaned, re.IGNORECASE):
                    # Check for company suffixes or good casing
                    if any(suf in cleaned.lower() for suf in ['inc', 'llc', 'ltd', 'corp', 'solutions', 'technologies', 'services', 'gmbh', 'co.', 'group', 'pvt']):
                        return {
                            'field_key': 'organization_name',
                            'field_label': 'Vendor / Organization',
                            'field_value': cleaned,
                            'original_value': cleaned,
                            'confidence': 88.0,
                            'field_type': 'organization',
                            'context_snippet': cleaned
                        }
        # If no explicit suffix found, use the first non-generic top line
        for line in lines[:3]:
            cleaned = line.strip()
            if len(cleaned) > 3 and not re.search(r'^(?:invoice|receipt|statement|page|\d+)', cleaned, re.IGNORECASE):
                return {
                    'field_key': 'organization_name',
                    'field_label': 'Vendor / Issuer',
                    'field_value': cleaned,
                    'original_value': cleaned,
                    'confidence': 72.0,
                    'field_type': 'organization',
                    'context_snippet': cleaned
                }
        return None

    @classmethod
    def _extract_person_name(cls, lines: List[str], category: str) -> Dict[str, Any]:
        # In invoices: "Bill To: [Name]", "Customer: [Name]"
        # In resumes: First line is usually the person's name
        if category == 'resume' and lines:
            first_line = lines[0].strip()
            if len(first_line.split()) in [2, 3, 4] and not any(ch in first_line for ch in '@:/#0123456789'):
                return {
                    'field_key': 'candidate_name',
                    'field_label': 'Candidate Name',
                    'field_value': first_line,
                    'original_value': first_line,
                    'confidence': 92.0,
                    'field_type': 'name',
                    'context_snippet': first_line
                }

        # Check for Bill To / Attention
        joined_text = "\n".join(lines[:20])
        bill_to_match = re.search(r'(?:bill\s*to|sold\s*to|recipient|attn|customer|client)[:\s]*([A-Za-z\s.\-]{3,40})', joined_text, re.IGNORECASE)
        if bill_to_match:
            val = bill_to_match.group(1).split('\n')[0].strip()
            if val and len(val) > 2:
                return {
                    'field_key': 'recipient_name',
                    'field_label': 'Recipient / Customer',
                    'field_value': val,
                    'original_value': val,
                    'confidence': 86.0,
                    'field_type': 'name',
                    'context_snippet': bill_to_match.group(0)
                }

        return None

    @classmethod
    def _extract_resume_fields(cls, text: str, lines: List[str]) -> List[Dict[str, Any]]:
        fields = []
        # Skills extraction
        skills_match = re.search(r'(?:skills|technical\s*skills|technologies|proficiencies)[:\s]*\n?([^\n]+(?:\n[^\n]+){1,4})', text, re.IGNORECASE)
        if skills_match:
            raw_skills = skills_match.group(1).strip().replace('\n', ', ')
            # trim length
            val = raw_skills[:200]
            fields.append({
                'field_key': 'skills',
                'field_label': 'Key Skills & Technologies',
                'field_value': val,
                'original_value': val,
                'confidence': 89.0,
                'field_type': 'string',
                'context_snippet': skills_match.group(0)[:150]
            })

        # Education degree
        degree_match = re.search(r'(?:bachelor|master|phd|b\.s\.|m\.s\.|b\.a\.|m\.a\.|degree\s*in)\s+[A-Za-z\s]+', text, re.IGNORECASE)
        if degree_match:
            degree_val = degree_match.group(0).strip()
            fields.append({
                'field_key': 'education',
                'field_label': 'Education / Degree',
                'field_value': degree_val,
                'original_value': degree_val,
                'confidence': 87.0,
                'field_type': 'string',
                'context_snippet': degree_val
            })

        return fields

    @classmethod
    def _extract_id_fields(cls, text: str, lines: List[str]) -> List[Dict[str, Any]]:
        fields = []
        # DOB
        dob_match = re.search(r'(?:dob|date\s*of\s*birth|birth\s*date)[:\s]*([0-9]{1,2}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{2,4})', text, re.IGNORECASE)
        if dob_match:
            dob_val = dob_match.group(1).strip()
            fields.append({
                'field_key': 'date_of_birth',
                'field_label': 'Date of Birth',
                'field_value': dob_val,
                'original_value': dob_val,
                'confidence': 94.0,
                'field_type': 'date',
                'context_snippet': dob_match.group(0)
            })

        # Expiry Date
        exp_match = re.search(r'(?:exp(?:iry)?\s*date|date\s*of\s*expiry|expires)[:\s]*([0-9]{1,2}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{2,4})', text, re.IGNORECASE)
        if exp_match:
            exp_val = exp_match.group(1).strip()
            fields.append({
                'field_key': 'expiry_date',
                'field_label': 'Expiration Date',
                'field_value': exp_val,
                'original_value': exp_val,
                'confidence': 93.0,
                'field_type': 'date',
                'context_snippet': exp_match.group(0)
            })

        # ID / License Number
        id_num_match = re.search(r'(?:passport\s*no\.?|license\s*no\.?|id\s*no\.?|card\s*number)[:\s]*([A-Z0-9\-_]{6,20})', text, re.IGNORECASE)
        if id_num_match:
            id_val = id_num_match.group(1).strip()
            fields.append({
                'field_key': 'id_number',
                'field_label': 'Document ID Number',
                'field_value': id_val,
                'original_value': id_val,
                'confidence': 92.0,
                'field_type': 'id_number',
                'context_snippet': id_num_match.group(0)
            })

        return fields
