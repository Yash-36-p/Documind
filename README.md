# 📄 DocuMind — Intelligent Document Processing Platform

DocuMind is an enterprise-grade document intelligence platform that automates extracting text, dates, financial amounts, invoice numbers, names, and structured entities from scanned documents, PDFs, and images. It provides hybrid OCR, automatic document classification, an interactive review and manual correction studio, high-speed multi-attribute search, CSV export, and role-based audit logging.

---

## 🌟 Key Features

1. **Document Upload & Ingestion**:
   - Supports **PDF**, **PNG**, **JPG**, **JPEG**, **WEBP**, and **TIFF** files up to 50MB.
   - Automatic MIME type detection, file size validation, and page counting.
   - Instant visual thumbnail generation for document cards and previews.

2. **Hybrid OCR Engine**:
   - **Direct Extraction via PyMuPDF (`fitz`)**: Lightning-fast, 98%+ character accuracy direct digital stream extraction for born-digital PDFs.
   - **Rasterized Tesseract OCR**: Automatically detects scanned/image-based PDF pages, renders them at 150+ DPI, enhances contrast with **Pillow**, and extracts text with character & word confidence metrics.
   - **Image OCR**: Direct preprocessing & OCR extraction for standalone photo scans and smartphone images.

3. **Multi-Category Document Classifier**:
   - Automated categorization into **Invoices**, **Receipts**, **Resumes / CVs**, **ID Documents**, **Contracts / Agreements**, **Certificates**, **Forms**, and **Reports**.
   - Weighted keyword distribution, header pattern detection, and regex structure cues.
   - Confidence score estimation and transparent signal explanations.

4. **Information Extraction Engine**:
   - Extracts structured key-value entities:
     - **Invoice & Reference #**: `invoice_number`, `order_number`, `id_number`
     - **Financials**: `total_amount`, `subtotal_amount`, `tax_amount`, currency symbols
     - **Dates**: `document_date`, `issue_date`, `due_date`, `date_of_birth`, `expiry_date`
     - **Vendor & Organization**: `organization_name`
     - **People & Contacts**: `candidate_name`, `recipient_name`, `email`, `phone`
     - **Domain-Specific**: Skills, education degrees, ID numbers, driver licenses

5. **Interactive Review & Manual Correction Studio**:
   - Side-by-side view: Document viewer on the left, structured field editor on the right.
   - Inline field editing with live save, undo, and delete.
   - Add custom fields on the fly.
   - Manual category override with 1-click update.
   - "Verify & Approve" review workflow.
   - Full chronological **Correction History** tracking who changed what from old to new values.
   - Full raw OCR text tab with one-click copy.

6. **Search & Analytics Dashboard**:
   - Full-text search across document titles, categories, raw OCR text, and extracted field values.
   - Analytics metrics: Total documents, processing success rate, average OCR quality, and accuracy rates.
   - 7-day ingestion and processing trend charts.

7. **Export & Audit Trails**:
   - Filtered or bulk **CSV Export** including all document metadata and structured extracted fields.
   - Immutable **Audit Logs** tracking every action: `UPLOAD`, `PROCESS_SUCCESS`, `FIELD_EDIT`, `CLASSIFICATION_CHANGE`, `VERIFY`, `DELETE`, and `EXPORT`.
   - Role-Based Access Control (**Admin**, **Reviewer**, **Viewer**).

---

## 🛠 Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, Vite, React Router v6 |
| **Styling** | Tailwind CSS v3, Lucide Icons |
| **API Client** | Axios with JWT interceptors |
| **Backend** | Python 3.14, Django 6.1, Django REST Framework 3.18 |
| **OCR & PDF** | Tesseract OCR v5.5, PyMuPDF v2.1, Pillow 13.0 |
| **Database** | PostgreSQL (or SQLite for zero-config dev) |
| **Background Tasks** | Celery 5.7, Redis |
| **Authentication** | SimpleJWT (JSON Web Tokens) |
| **API Documentation**| Swagger & OpenAPI via `drf-spectacular` |

---

## 🚀 Quick Start

### Option 1: One-Click Launch Script
Run the automated launcher script from the root directory:
```bash
./start_dev.sh
```
This runs migrations, seeds sample documents, and boots both the Django API (`http://127.0.0.1:8000`) and the React UI (`http://localhost:3000`).

---

### Option 2: Manual Step-by-Step Setup

#### 1. Backend Setup
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt # (if needed)

# Apply migrations
python manage.py migrate

# Seed initial demo users & documents
python manage.py seed_data

# Start backend server
python manage.py runserver 0.0.0.0:8000
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser.

#### 3. (Optional) Run Celery Worker
```bash
cd backend
./run_celery.sh
```

---

## 🔑 Demo Accounts

DocuMind comes pre-configured with 3 role accounts. On the Login screen, click any of the 1-click fill buttons:

| Role | Username | Password | Permissions |
|---|---|---|---|
| **Admin** | `admin` | `admin123` | Full access: manage users, delete documents, edit fields, verify, export |
| **Reviewer** | `reviewer` | `reviewer123` | Upload, edit fields, verify extractions, override categories, export |
| **Viewer** | `viewer` | `viewer123` | Read-only inspection, search, and CSV export |

---

## 📚 Interactive API Documentation (Swagger)

DocuMind provides interactive OpenAPI / Swagger UI:
- **Swagger UI**: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **ReDoc**: [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)
- **Schema JSON**: [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)

### Core API Endpoints
- `POST /api/auth/login/` - JWT login
- `POST /api/auth/register/` - Register new user
- `GET /api/documents/` - List documents (supports `?search=`, `?category=`, `?status=`, `?verified=`)
- `POST /api/documents/` - Upload document (PDF, PNG, JPG)
- `GET /api/documents/<id>/` - Retrieve document details, pages, fields, and correction history
- `POST /api/documents/<id>/reprocess/` - Re-trigger OCR extraction pipeline
- `POST /api/documents/<id>/verify/` - Mark document verified or revoke verification
- `PATCH /api/documents/<id>/category/` - Manually override document classification
- `GET /api/documents/<id>/download/` - Download original document file
- `GET /api/documents/<id>/fields/` - List extracted fields
- `POST /api/documents/<id>/fields/` - Add custom field
- `PATCH /api/fields/<id>/` - Update/correct field value (creates audit log)
- `DELETE /api/fields/<id>/` - Delete field
- `GET /api/analytics/dashboard/` - Analytics metrics & category distribution
- `GET /api/search/?q=` - Global multi-attribute text search
- `GET /api/export/csv/` - Export documents and fields to CSV
- `GET /api/audit/logs/` - Immutable audit logs

---

## 🏛 Architecture & Project Layout

```
DocuMind/
├── backend/
│   ├── apps/
│   │   ├── users/            # Module 1: Auth, JWT, User Roles
│   │   ├── documents/        # Module 2: Document Model, Upload, Storage, Celery Tasks
│   │   ├── ocr/              # Module 3: Hybrid OCR (PyMuPDF + Tesseract + Pillow)
│   │   ├── extraction/       # Module 4 & 6: Entity Extractor, Field Model, Correction History
│   │   ├── classification/   # Module 5: Rule-based & regex Category Classifier
│   │   ├── audit/            # Module 7: Immutable Audit Logging Engine
│   │   └── analytics/        # Module 7: Search & CSV Export
│   ├── config/               # Settings, Celery, URLs, DRF & CORS configuration
│   ├── media/                # Storage for uploaded files and rendered thumbnails
│   ├── manage.py
│   └── run_celery.sh
├── frontend/
│   ├── src/
│   │   ├── api/client.js     # Axios with JWT interceptors
│   │   ├── context/          # AuthContext with role-based state
│   │   ├── components/       # Navbar, Sidebar, Layout, UploadModal
│   │   ├── pages/            # Dashboard, Documents, DocumentReview, Search, AuditLogs, Login, Register
│   │   ├── App.jsx           # Routing & Guards
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── start_dev.sh              # One-click platform launcher
└── README.md
```
