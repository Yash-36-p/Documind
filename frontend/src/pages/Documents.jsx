import React, { useState, useEffect } from 'react';
import { Link, useOutletContext } from 'react-router-dom';
import api, { API_BASE_URL, resolveMediaUrl } from '../api/client';
import { useAuth } from '../context/AuthContext';
import {
  FileText,
  Search,
  Filter,
  RefreshCw,
  Trash2,
  Download,
  UploadCloud,
  FileSpreadsheet,
  CheckCircle2,
  Clock,
  AlertCircle,
  Eye,
  SlidersHorizontal,
  ChevronRight
} from 'lucide-react';

const CATEGORIES = [
  { value: 'all', label: 'All Categories' },
  { value: 'invoice', label: 'Invoices' },
  { value: 'receipt', label: 'Receipts' },
  { value: 'resume', label: 'Resumes / CV' },
  { value: 'id_card', label: 'ID Documents' },
  { value: 'contract', label: 'Contracts' },
  { value: 'certificate', label: 'Certificates' },
  { value: 'form', label: 'Forms' },
  { value: 'report', label: 'Reports' },
  { value: 'other', label: 'Other' },
];

const STATUSES = [
  { value: 'all', label: 'All Statuses' },
  { value: 'completed', label: 'Completed' },
  { value: 'processing', label: 'Processing' },
  { value: 'failed', label: 'Failed' },
  { value: 'pending', label: 'Pending' },
];

export default function Documents() {
  const { openUpload } = useOutletContext();
  const { isReviewer, isAdmin } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [verifiedFilter, setVerifiedFilter] = useState('all');
  const [minConfidence, setMinConfidence] = useState('');
  const [reprocessingId, setReprocessingId] = useState(null);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (category !== 'all') params.append('category', category);
      if (statusFilter !== 'all') params.append('status', statusFilter);
      if (verifiedFilter !== 'all') params.append('verified', verifiedFilter);
      if (minConfidence) params.append('min_confidence', minConfidence);

      const res = await api.get(`/documents/?${params.toString()}`);
      setDocuments(res.data.results || res.data);
    } catch (err) {
      console.error('Failed to fetch documents:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      fetchDocuments();
    }, 250);
    return () => clearTimeout(delayDebounce);
  }, [search, category, statusFilter, verifiedFilter, minConfidence]);

  const handleReprocess = async (docId, e) => {
    e.preventDefault();
    e.stopPropagation();
    setReprocessingId(docId);
    try {
      await api.post(`/documents/${docId}/reprocess/`);
      await fetchDocuments();
    } catch (err) {
      console.error('Reprocess failed:', err);
    } finally {
      setReprocessingId(null);
    }
  };

  const handleDelete = async (docId, title, e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!window.confirm(`Are you sure you want to delete "${title}"?`)) return;

    try {
      await api.delete(`/documents/${docId}/`);
      setDocuments(documents.filter((d) => d.id !== docId));
    } catch (err) {
      console.error('Delete failed:', err);
      alert('Failed to delete document.');
    }
  };

  const handleExportCsv = () => {
    const params = new URLSearchParams();
    if (category !== 'all') params.append('category', category);
    if (statusFilter !== 'all') params.append('status', statusFilter);
    if (verifiedFilter !== 'all') params.append('verified', verifiedFilter);
    window.open(`${API_BASE_URL}/export/csv/?${params.toString()}`, '_blank');
  };

  const formatSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900 md:text-3xl">
            Document Repository
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Search, filter, review extractions, and export processed document batches.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleExportCsv}
            className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50"
          >
            <FileSpreadsheet className="h-4 w-4 text-emerald-600" />
            <span>Export CSV</span>
          </button>
          {isReviewer && (
            <button
              onClick={openUpload}
              className="flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm shadow-indigo-600/30 transition hover:bg-indigo-700"
            >
              <UploadCloud className="h-4 w-4" />
              <span>Upload Document</span>
            </button>
          )}
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm space-y-4">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center">
          {/* Search Input */}
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-2.5 h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search by title, invoice #, amounts, vendor, extracted text..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-xl border border-slate-200 bg-slate-50/50 py-2 pl-10 pr-4 text-sm text-slate-800 placeholder-slate-400 focus:border-indigo-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-100"
            />
          </div>

          {/* Category Filter */}
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-100"
          >
            {CATEGORIES.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </select>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-100"
          >
            {STATUSES.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>

          {/* Verified Filter */}
          <select
            value={verifiedFilter}
            onChange={(e) => setVerifiedFilter(e.target.value)}
            className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-100"
          >
            <option value="all">All Verification</option>
            <option value="true">Verified Only</option>
            <option value="false">Needs Review</option>
          </select>

          {/* Refresh button */}
          <button
            onClick={fetchDocuments}
            disabled={loading}
            className="flex items-center gap-1.5 rounded-xl border border-slate-200 px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50"
            title="Refresh list"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Document Grid / Table */}
      <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="border-b border-slate-100 bg-slate-50/70 text-[11px] font-bold uppercase tracking-wider text-slate-400">
              <tr>
                <th className="px-6 py-3.5">Document Details</th>
                <th className="px-6 py-3.5">Category</th>
                <th className="px-6 py-3.5">Processing Status</th>
                <th className="px-6 py-3.5">OCR Quality</th>
                <th className="px-6 py-3.5">Verification</th>
                <th className="px-6 py-3.5">Date Ingested</th>
                <th className="px-6 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="7" className="py-12 text-center text-sm text-slate-400">
                    <RefreshCw className="mx-auto h-6 w-6 animate-spin text-indigo-500 mb-2" />
                    Loading documents...
                  </td>
                </tr>
              ) : documents && documents.length > 0 ? (
                documents.map((doc) => (
                  <tr key={doc.id} className="transition hover:bg-slate-50/80">
                    {/* Document details & thumbnail */}
                    <td className="px-6 py-4">
                      <Link to={`/documents/${doc.id}`} className="flex items-center gap-3.5 group">
                        <div className="relative flex h-12 w-12 shrink-0 items-center justify-center overflow-hidden rounded-xl border border-slate-200 bg-slate-100 group-hover:border-indigo-300 transition">
                          {doc.preview_url ? (
                            <img
                              src={resolveMediaUrl(doc.preview_url)}
                              alt={doc.title}
                              className="h-full w-full object-cover"
                            />
                          ) : (
                            <FileText className="h-6 w-6 text-slate-400 group-hover:text-indigo-600" />
                          )}
                        </div>
                        <div>
                          <div className="font-bold text-slate-900 group-hover:text-indigo-600 transition">
                            {doc.title}
                          </div>
                          <div className="text-xs text-slate-400">
                            {doc.filename} • {formatSize(doc.file_size)} • {doc.page_count} {doc.page_count === 1 ? 'page' : 'pages'}
                          </div>
                        </div>
                      </Link>
                    </td>

                    {/* Category */}
                    <td className="px-6 py-4">
                      <div className="inline-block">
                        <span className="rounded-lg bg-indigo-50 px-2.5 py-1 text-xs font-semibold text-indigo-700">
                          {doc.category_display || doc.category}
                        </span>
                        <div className="text-[11px] text-slate-400 mt-0.5">
                          {doc.classification_confidence}% match
                        </div>
                      </div>
                    </td>

                    {/* Status */}
                    <td className="px-6 py-4">
                      {doc.status === 'completed' && (
                        <span className="inline-flex items-center gap-1 rounded-md bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">
                          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" /> Completed
                        </span>
                      )}
                      {doc.status === 'processing' && (
                        <span className="inline-flex items-center gap-1 rounded-md bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700">
                          <Clock className="h-3.5 w-3.5 animate-spin text-blue-600" /> Extracting...
                        </span>
                      )}
                      {doc.status === 'failed' && (
                        <span className="inline-flex items-center gap-1 rounded-md bg-rose-50 px-2.5 py-1 text-xs font-medium text-rose-700">
                          <AlertCircle className="h-3.5 w-3.5 text-rose-600" /> Failed
                        </span>
                      )}
                      {doc.status === 'pending' && (
                        <span className="inline-flex items-center gap-1 rounded-md bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">
                          Pending
                        </span>
                      )}
                    </td>

                    {/* OCR Quality */}
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="h-2 w-16 overflow-hidden rounded-full bg-slate-100">
                          <div
                            className={`h-full ${
                              doc.ocr_confidence >= 85
                                ? 'bg-emerald-500'
                                : doc.ocr_confidence >= 60
                                ? 'bg-amber-500'
                                : 'bg-rose-500'
                            }`}
                            style={{ width: `${doc.ocr_confidence}%` }}
                          />
                        </div>
                        <span className="text-xs font-bold text-slate-700">
                          {doc.ocr_confidence}%
                        </span>
                      </div>
                    </td>

                    {/* Verification */}
                    <td className="px-6 py-4">
                      {doc.is_verified ? (
                        <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-700">
                          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
                          Verified
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2.5 py-0.5 text-xs font-semibold text-amber-700">
                          Needs Review
                        </span>
                      )}
                    </td>

                    {/* Date */}
                    <td className="px-6 py-4 text-xs text-slate-500">
                      {new Date(doc.created_at).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric'
                      })}
                    </td>

                    {/* Actions */}
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <Link
                          to={`/documents/${doc.id}`}
                          className="rounded-lg p-1.5 text-slate-400 hover:bg-indigo-50 hover:text-indigo-600 transition"
                          title="Review & Correct"
                        >
                          <Eye className="h-4 w-4" />
                        </Link>

                        {isReviewer && (
                          <button
                            onClick={(e) => handleReprocess(doc.id, e)}
                            disabled={reprocessingId === doc.id}
                            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition"
                            title="Reprocess OCR & Fields"
                          >
                            <RefreshCw
                              className={`h-4 w-4 ${reprocessingId === doc.id ? 'animate-spin text-indigo-600' : ''}`}
                            />
                          </button>
                        )}

                        <a
                          href={`${API_BASE_URL}/documents/${doc.id}/download/`}
                          target="_blank"
                          rel="noreferrer"
                          className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition"
                          title="Download original"
                        >
                          <Download className="h-4 w-4" />
                        </a>

                        {isAdmin && (
                          <button
                            onClick={(e) => handleDelete(doc.id, doc.title, e)}
                            className="rounded-lg p-1.5 text-slate-400 hover:bg-rose-50 hover:text-rose-600 transition"
                            title="Delete"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7" className="py-12 text-center text-sm text-slate-400">
                    No matching documents found. Try clearing filters or upload a new file.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

