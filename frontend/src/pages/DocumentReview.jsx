import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api, { API_BASE_URL } from '../api/client';
import { useAuth } from '../context/AuthContext';
import {
  FileText,
  CheckCircle2,
  AlertCircle,
  Clock,
  Download,
  RefreshCw,
  Edit3,
  Trash2,
  Plus,
  Save,
  Undo2,
  Copy,
  ChevronLeft,
  ChevronRight,
  ZoomIn,
  ZoomOut,
  Maximize2,
  ExternalLink,
  ShieldCheck,
  History,
  Sparkles,
  Layers,
  FileSpreadsheet,
  Check,
  X
} from 'lucide-react';

const CATEGORY_OPTIONS = [
  { value: 'invoice', label: 'Invoice' },
  { value: 'receipt', label: 'Receipt' },
  { value: 'resume', label: 'Resume / CV' },
  { value: 'id_card', label: 'ID Document' },
  { value: 'contract', label: 'Contract / Agreement' },
  { value: 'certificate', label: 'Certificate' },
  { value: 'form', label: 'Form' },
  { value: 'report', label: 'Report' },
  { value: 'other', label: 'Other' },
];

export default function DocumentReview() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isReviewer, isAdmin } = useAuth();

  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('fields'); // 'fields', 'history', 'raw_text'
  const [activePage, setActivePage] = useState(1);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [reprocessing, setReprocessing] = useState(false);
  const [verifying, setVerifying] = useState(false);

  // Field editing state
  const [editedFields, setEditedFields] = useState({});
  const [savingFieldId, setSavingFieldId] = useState(null);
  const [copyFeedback, setCopyFeedback] = useState(false);

  // Add Custom Field modal
  const [showAddField, setShowAddField] = useState(false);
  const [newFieldKey, setNewFieldKey] = useState('');
  const [newFieldLabel, setNewFieldLabel] = useState('');
  const [newFieldValue, setNewFieldValue] = useState('');
  const [newFieldType, setNewFieldType] = useState('string');

  const fetchDocument = async () => {
    try {
      const res = await api.get(`/documents/${id}/`);
      setDocument(res.data);
      // Initialize edited fields map
      const initialMap = {};
      if (res.data.fields) {
        res.data.fields.forEach((f) => {
          initialMap[f.id] = f.field_value;
        });
      }
      setEditedFields(initialMap);
    } catch (err) {
      console.error('Failed to fetch document:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocument();
  }, [id]);

  const handleFieldValueChange = (fieldId, value) => {
    setEditedFields((prev) => ({ ...prev, [fieldId]: value }));
  };

  const handleSaveField = async (field) => {
    const newVal = editedFields[field.id];
    if (newVal === field.field_value) return;

    setSavingFieldId(field.id);
    try {
      await api.patch(`/fields/${field.id}/`, {
        field_value: newVal,
        notes: 'Manual review adjustment',
      });
      await fetchDocument();
    } catch (err) {
      console.error('Failed to update field:', err);
      alert('Failed to save field value.');
    } finally {
      setSavingFieldId(null);
    }
  };

  const handleDeleteField = async (fieldId) => {
    if (!window.confirm('Are you sure you want to delete this field?')) return;
    try {
      await api.delete(`/fields/${fieldId}/`);
      await fetchDocument();
    } catch (err) {
      console.error('Failed to delete field:', err);
    }
  };

  const handleAddFieldSubmit = async (e) => {
    e.preventDefault();
    if (!newFieldLabel || !newFieldValue) return;

    try {
      const key = newFieldKey || newFieldLabel.toLowerCase().replace(/[^a-z0-9]/g, '_');
      await api.post(`/documents/${id}/fields/`, {
        field_key: key,
        field_label: newFieldLabel,
        field_value: newFieldValue,
        field_type: newFieldType,
      });
      setShowAddField(false);
      setNewFieldKey('');
      setNewFieldLabel('');
      setNewFieldValue('');
      await fetchDocument();
    } catch (err) {
      console.error('Failed to add custom field:', err);
      alert('Failed to add custom field.');
    }
  };

  const handleCategoryChange = async (newCategory) => {
    try {
      await api.patch(`/documents/${id}/category/`, { category: newCategory });
      await fetchDocument();
    } catch (err) {
      console.error('Failed to update category:', err);
    }
  };

  const handleToggleVerify = async () => {
    setVerifying(true);
    try {
      await api.post(`/documents/${id}/verify/`, {
        is_verified: !document.is_verified,
      });
      await fetchDocument();
    } catch (err) {
      console.error('Failed to verify document:', err);
    } finally {
      setVerifying(false);
    }
  };

  const handleReprocess = async () => {
    setReprocessing(true);
    try {
      await api.post(`/documents/${id}/reprocess/`);
      await fetchDocument();
    } catch (err) {
      console.error('Reprocess failed:', err);
    } finally {
      setReprocessing(false);
    }
  };

  const handleCopyRawText = () => {
    if (!document?.raw_text) return;
    navigator.clipboard.writeText(document.raw_text);
    setCopyFeedback(true);
    setTimeout(() => setCopyFeedback(false), 2000);
  };

  const getConfidenceColor = (conf) => {
    if (conf >= 85) return 'text-emerald-600 bg-emerald-50 border-emerald-200';
    if (conf >= 60) return 'text-amber-600 bg-amber-50 border-amber-200';
    return 'text-rose-600 bg-rose-50 border-rose-200';
  };

  if (loading) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center space-y-3">
        <RefreshCw className="h-8 w-8 animate-spin text-indigo-600" />
        <p className="text-sm font-semibold text-slate-600">Loading document intelligence studio...</p>
      </div>
    );
  }

  if (!document) {
    return (
      <div className="rounded-2xl border border-red-200 bg-red-50 p-8 text-center">
        <AlertCircle className="mx-auto h-8 w-8 text-red-500 mb-2" />
        <h3 className="text-base font-bold text-red-800">Document Not Found</h3>
        <p className="text-sm text-red-600 mt-1">This document does not exist or has been removed.</p>
        <Link to="/documents" className="mt-4 inline-block text-xs font-bold text-indigo-600 hover:underline">
          Return to Documents
        </Link>
      </div>
    );
  }

  const currentPageData = document.pages?.find((p) => p.page_number === activePage);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Top Header & Breadcrumb */}
      <div className="flex flex-col gap-4 border-b border-slate-200 pb-5 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/documents')}
            className="flex h-9 w-9 items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 transition"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-extrabold text-slate-900 md:text-2xl">
                {document.title}
              </h1>
              {document.is_verified && (
                <span className="flex items-center gap-1 rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-bold text-emerald-800">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" /> Verified
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              {document.filename} • {document.file_type.toUpperCase()} • {document.page_count} pages • Ingested {new Date(document.created_at).toLocaleString()}
            </p>
          </div>
        </div>

        {/* Global actions: Verify, Reprocess, Export, Download */}
        <div className="flex flex-wrap items-center gap-2.5">
          {isReviewer && (
            <button
              onClick={handleToggleVerify}
              disabled={verifying}
              className={`flex items-center gap-1.5 rounded-xl px-4 py-2 text-xs font-bold transition shadow-sm ${
                document.is_verified
                  ? 'border border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
                  : 'bg-emerald-600 text-white shadow-emerald-600/20 hover:bg-emerald-700'
              }`}
            >
              <CheckCircle2 className="h-4 w-4" />
              <span>{document.is_verified ? 'Revoke Verification' : 'Verify & Approve'}</span>
            </button>
          )}

          {isReviewer && (
            <button
              onClick={handleReprocess}
              disabled={reprocessing}
              className="flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition"
              title="Re-run OCR and extraction"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${reprocessing ? 'animate-spin text-indigo-600' : ''}`} />
              <span>Reprocess</span>
            </button>
          )}

          <a
            href={`/api/export/csv/?doc_id=${document.id}`}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition"
          >
            <FileSpreadsheet className="h-3.5 w-3.5 text-emerald-600" />
            <span>CSV</span>
          </a>

          <a
            href={`/api/documents/${document.id}/download/`}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition"
          >
            <Download className="h-3.5 w-3.5" />
            <span>Download</span>
          </a>
        </div>
      </div>

      {/* Main Split Layout: Left = Document Visual Viewer, Right = Extraction Studio */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12 items-start">
        {/* LEFT COLUMN: Visual Document Viewer (5 cols) */}
        <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden lg:col-span-5 flex flex-col">
          {/* Viewer Toolbar */}
          <div className="flex items-center justify-between border-b border-slate-100 bg-slate-50/80 px-4 py-2.5">
            {/* Page navigation */}
            <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-600">
              <button
                disabled={activePage <= 1}
                onClick={() => setActivePage((p) => Math.max(1, p - 1))}
                className="rounded p-1 hover:bg-slate-200 disabled:opacity-30"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <span>
                Page {activePage} of {document.page_count}
              </span>
              <button
                disabled={activePage >= document.page_count}
                onClick={() => setActivePage((p) => Math.min(document.page_count, p + 1))}
                className="rounded p-1 hover:bg-slate-200 disabled:opacity-30"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>

            {/* Zoom Controls */}
            <div className="flex items-center gap-1 text-slate-500">
              <button
                onClick={() => setZoomLevel((z) => Math.max(0.6, z - 0.2))}
                className="rounded p-1 hover:bg-slate-200"
                title="Zoom Out"
              >
                <ZoomOut className="h-4 w-4" />
              </button>
              <span className="text-[11px] font-bold w-10 text-center">
                {Math.round(zoomLevel * 100)}%
              </span>
              <button
                onClick={() => setZoomLevel((z) => Math.min(2.5, z + 0.2))}
                className="rounded p-1 hover:bg-slate-200"
                title="Zoom In"
              >
                <ZoomIn className="h-4 w-4" />
              </button>
              <button
                onClick={() => setZoomLevel(1)}
                className="rounded px-1.5 py-0.5 text-[10px] font-semibold hover:bg-slate-200"
              >
                Reset
              </button>
            </div>
          </div>

          {/* Rendered Preview Container */}
          <div className="relative min-h-[500px] max-h-[720px] overflow-auto bg-slate-900/5 p-4 flex items-center justify-center">
            {currentPageData?.thumbnail_url || document.preview_url ? (
              <div
                style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'top center' }}
                className="transition-transform duration-150 shadow-lg rounded-lg overflow-hidden bg-white max-w-full"
              >
                <img
                  src={currentPageData?.thumbnail_url || document.preview_url}
                  alt={`Page ${activePage}`}
                  className="max-h-[680px] w-auto object-contain mx-auto"
                />
              </div>
            ) : document.file_url && document.file_type === 'pdf' ? (
              <iframe
                src={`${document.file_url}#page=${activePage}`}
                className="h-[650px] w-full rounded-lg border border-slate-200"
                title="PDF Document"
              />
            ) : (
              <div className="flex flex-col items-center justify-center py-16 text-slate-400">
                <FileText className="h-12 w-12 stroke-[1.5] mb-2 text-slate-300" />
                <p className="text-xs">No visual preview available.</p>
                <a
                  href={`/api/documents/${document.id}/download/`}
                  className="mt-2 text-xs font-semibold text-indigo-600 hover:underline"
                >
                  Download file to inspect
                </a>
              </div>
            )}
          </div>

          {/* Page OCR method footnote */}
          {currentPageData && (
            <div className="flex items-center justify-between border-t border-slate-100 bg-slate-50 px-4 py-2 text-[11px] text-slate-500">
              <span>
                Method: <strong className="text-slate-700">{currentPageData.extraction_method}</strong>
              </span>
              <span>
                Confidence: <strong className="text-slate-700">{currentPageData.ocr_confidence}%</strong>
              </span>
            </div>
          )}
        </div>

        {/* RIGHT COLUMN: Extraction & Review Studio (7 cols) */}
        <div className="space-y-6 lg:col-span-7">
          {/* Classification & Confidence Banner */}
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div>
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                  Document Classification
                </span>
                <div className="mt-1 flex items-center gap-2">
                  <span className="text-lg font-bold text-slate-900">
                    {document.category_display || document.category}
                  </span>
                  <span className="rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-bold text-indigo-700">
                    {document.classification_confidence}% confidence
                  </span>
                </div>
              </div>

              {/* Category Override Select */}
              {isReviewer && (
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-500">Override:</span>
                  <select
                    value={document.category}
                    onChange={(e) => handleCategoryChange(e.target.value)}
                    className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-700 focus:border-indigo-500 focus:bg-white focus:outline-none"
                  >
                    {CATEGORY_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>

            {/* Clues & Explanation */}
            {document.classification_explanation?.clues && (
              <div className="flex flex-wrap items-center gap-1.5 pt-1 border-t border-slate-100 text-[11px] text-slate-500">
                <span className="font-semibold text-slate-400">Detected Signals:</span>
                {document.classification_explanation.clues.map((clue, idx) => (
                  <span key={idx} className="rounded-md bg-slate-100 px-2 py-0.5 text-slate-600 font-mono text-[10px]">
                    {clue}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Interactive Studio Tabs */}
          <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
            {/* Tab Switcher */}
            <div className="flex items-center justify-between border-b border-slate-200 px-6 pt-3 bg-slate-50/50">
              <div className="flex gap-6">
                <button
                  onClick={() => setActiveTab('fields')}
                  className={`pb-3 text-sm font-bold transition border-b-2 ${
                    activeTab === 'fields'
                      ? 'border-indigo-600 text-indigo-600'
                      : 'border-transparent text-slate-500 hover:text-slate-800'
                  }`}
                >
                  Extracted Fields ({document.fields?.length || 0})
                </button>
                <button
                  onClick={() => setActiveTab('history')}
                  className={`pb-3 text-sm font-bold transition border-b-2 ${
                    activeTab === 'history'
                      ? 'border-indigo-600 text-indigo-600'
                      : 'border-transparent text-slate-500 hover:text-slate-800'
                  }`}
                >
                  Correction History ({document.correction_logs?.length || 0})
                </button>
                <button
                  onClick={() => setActiveTab('raw_text')}
                  className={`pb-3 text-sm font-bold transition border-b-2 ${
                    activeTab === 'raw_text'
                      ? 'border-indigo-600 text-indigo-600'
                      : 'border-transparent text-slate-500 hover:text-slate-800'
                  }`}
                >
                  Raw OCR Text
                </button>
              </div>

              {activeTab === 'fields' && isReviewer && (
                <button
                  onClick={() => setShowAddField(true)}
                  className="mb-2 flex items-center gap-1.5 rounded-lg bg-indigo-50 px-3 py-1.5 text-xs font-bold text-indigo-600 hover:bg-indigo-100 transition"
                >
                  <Plus className="h-3.5 w-3.5" />
                  <span>Add Field</span>
                </button>
              )}
            </div>

            {/* TAB 1: EXTRACTED FIELDS (REVIEW & CORRECTION) */}
            {activeTab === 'fields' && (
              <div className="p-6 space-y-4">
                {document.fields && document.fields.length > 0 ? (
                  document.fields.map((field) => {
                    const isDirty = editedFields[field.id] !== field.field_value;
                    const isSaving = savingFieldId === field.id;

                    return (
                      <div
                        key={field.id}
                        className="rounded-xl border border-slate-200 p-4 transition hover:border-slate-300 space-y-2 bg-white"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <label className="text-xs font-bold text-slate-800">
                              {field.field_label}
                            </label>
                            <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-mono text-slate-500 uppercase">
                              {field.field_type}
                            </span>
                            {field.is_corrected && (
                              <span className="rounded bg-amber-50 px-1.5 py-0.5 text-[10px] font-bold text-amber-700">
                                Edited
                              </span>
                            )}
                          </div>

                          {/* Confidence score badge */}
                          <div className="flex items-center gap-1.5">
                            <span
                              className={`rounded-full border px-2 py-0.5 text-[10px] font-bold ${getConfidenceColor(
                                field.confidence
                              )}`}
                            >
                              {field.confidence}% Match
                            </span>
                            {isAdmin && (
                              <button
                                onClick={() => handleDeleteField(field.id)}
                                className="rounded p-1 text-slate-400 hover:bg-rose-50 hover:text-rose-600 transition"
                                title="Delete field"
                              >
                                <Trash2 className="h-3.5 w-3.5" />
                              </button>
                            )}
                          </div>
                        </div>

                        {/* Field input and inline actions */}
                        <div className="flex items-center gap-2">
                          <input
                            type="text"
                            value={editedFields[field.id] ?? field.field_value}
                            onChange={(e) => handleFieldValueChange(field.id, e.target.value)}
                            disabled={!isReviewer}
                            className={`flex-1 rounded-xl border px-3.5 py-2 text-sm text-slate-900 transition focus:outline-none focus:ring-2 focus:ring-indigo-100 ${
                              isDirty
                                ? 'border-amber-400 bg-amber-50/20'
                                : 'border-slate-200 bg-slate-50/50 focus:border-indigo-500 focus:bg-white'
                            }`}
                          />

                          {isDirty && (
                            <>
                              <button
                                onClick={() => handleSaveField(field)}
                                disabled={isSaving}
                                className="flex items-center gap-1 rounded-xl bg-indigo-600 px-3 py-2 text-xs font-bold text-white shadow-sm hover:bg-indigo-700 transition"
                                title="Save correction"
                              >
                                <Save className="h-3.5 w-3.5" />
                                <span>Save</span>
                              </button>
                              <button
                                onClick={() =>
                                  setEditedFields((prev) => ({
                                    ...prev,
                                    [field.id]: field.field_value,
                                  }))
                                }
                                className="rounded-xl border border-slate-200 px-2.5 py-2 text-xs font-semibold text-slate-500 hover:bg-slate-50 transition"
                                title="Reset changes"
                              >
                                <Undo2 className="h-3.5 w-3.5" />
                              </button>
                            </>
                          )}
                        </div>

                        {/* Show original value if edited */}
                        {field.is_corrected && field.original_value && (
                          <div className="text-[11px] text-slate-400">
                            Original OCR extraction:{' '}
                            <span className="font-mono text-slate-600 line-through">
                              {field.original_value}
                            </span>
                          </div>
                        )}
                      </div>
                    );
                  })
                ) : (
                  <div className="py-12 text-center text-sm text-slate-400">
                    No fields extracted yet. Click "Add Field" to create one or reprocess document.
                  </div>
                )}
              </div>
            )}

            {/* TAB 2: CORRECTION HISTORY */}
            {activeTab === 'history' && (
              <div className="p-6">
                {document.correction_logs && document.correction_logs.length > 0 ? (
                  <div className="relative border-l border-slate-200 pl-6 space-y-6">
                    {document.correction_logs.map((log) => (
                      <div key={log.id} className="relative space-y-1">
                        <span className="absolute -left-[31px] top-1 flex h-4 w-4 items-center justify-center rounded-full bg-indigo-600 ring-4 ring-white" />
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-bold text-slate-800">
                            {log.field_label || log.field_key}
                          </span>
                          <span className="text-[11px] text-slate-400">
                            {new Date(log.corrected_at).toLocaleString()}
                          </span>
                        </div>
                        <div className="rounded-xl bg-slate-50 p-3 text-xs text-slate-700 font-mono space-y-1">
                          <div className="text-rose-600 line-through">
                            - {log.previous_value || '(empty)'}
                          </div>
                          <div className="text-emerald-600 font-bold">
                            + {log.new_value}
                          </div>
                        </div>
                        <div className="text-[11px] text-slate-500">
                          By <strong className="text-slate-700">{log.corrected_by_name}</strong> •{' '}
                          <span className="capitalize">{log.correction_type.replace('_', ' ')}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="py-12 text-center text-sm text-slate-400">
                    No manual corrections recorded. All fields are in their original AI-extracted state.
                  </p>
                )}
              </div>
            )}

            {/* TAB 3: RAW OCR & PYMUPDF EXTRACTED TEXT */}
            {activeTab === 'raw_text' && (
              <div className="p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-500">
                    Full text stream ({document.raw_text?.length || 0} characters)
                  </span>
                  <button
                    onClick={handleCopyRawText}
                    className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-bold text-slate-700 hover:bg-slate-50 transition"
                  >
                    {copyFeedback ? (
                      <>
                        <Check className="h-3.5 w-3.5 text-emerald-600" />
                        <span>Copied!</span>
                      </>
                    ) : (
                      <>
                        <Copy className="h-3.5 w-3.5 text-slate-500" />
                        <span>Copy All</span>
                      </>
                    )}
                  </button>
                </div>

                <pre className="max-h-[500px] overflow-auto rounded-xl bg-slate-900 p-4 text-xs font-mono text-slate-200 leading-relaxed whitespace-pre-wrap selection:bg-indigo-500">
                  {document.raw_text || 'No text extracted.'}
                </pre>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Add Custom Field Modal */}
      {showAddField && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-sm animate-in fade-in">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900">Add Custom Field</h3>
              <button
                onClick={() => setShowAddField(false)}
                className="rounded p-1 text-slate-400 hover:bg-slate-100"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleAddFieldSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
                  Field Label
                </label>
                <input
                  type="text"
                  placeholder="e.g. Purchase Order #"
                  value={newFieldLabel}
                  onChange={(e) => setNewFieldLabel(e.target.value)}
                  required
                  className="w-full rounded-xl border border-slate-200 px-3.5 py-2 text-sm text-slate-800 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
                  Field Value
                </label>
                <input
                  type="text"
                  placeholder="e.g. PO-99201"
                  value={newFieldValue}
                  onChange={(e) => setNewFieldValue(e.target.value)}
                  required
                  className="w-full rounded-xl border border-slate-200 px-3.5 py-2 text-sm text-slate-800 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
                  Field Type
                </label>
                <select
                  value={newFieldType}
                  onChange={(e) => setNewFieldType(e.target.value)}
                  className="w-full rounded-xl border border-slate-200 px-3.5 py-2 text-sm text-slate-800 focus:border-indigo-500 focus:outline-none"
                >
                  <option value="string">Text</option>
                  <option value="currency">Currency / Amount</option>
                  <option value="date">Date</option>
                  <option value="id_number">ID / Ref #</option>
                  <option value="email">Email</option>
                  <option value="phone">Phone</option>
                  <option value="organization">Organization</option>
                </select>
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddField(false)}
                  className="rounded-xl border border-slate-200 px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded-xl bg-indigo-600 px-4 py-2 text-xs font-bold text-white shadow-sm hover:bg-indigo-700"
                >
                  Create Field
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

