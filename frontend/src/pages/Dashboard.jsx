import React, { useState, useEffect } from 'react';
import { Link, useOutletContext } from 'react-router-dom';
import api, { API_BASE_URL } from '../api/client';
import {
  FileText,
  CheckCircle2,
  Clock,
  AlertCircle,
  TrendingUp,
  ShieldCheck,
  UploadCloud,
  FileSpreadsheet,
  ArrowUpRight,
  Sparkles,
  BarChart3,
  Layers
} from 'lucide-react';

export default function Dashboard() {
  const { openUpload } = useOutletContext();
  const [stats, setStats] = useState(null);
  const [recentDocs, setRecentDocs] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, docsRes] = await Promise.all([
        api.get('/analytics/dashboard/'),
        api.get('/documents/?limit=5')
      ]);
      setStats(statsRes.data);
      setRecentDocs(docsRes.data.results || docsRes.data);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleExportCsv = () => {
    window.open(`${API_BASE_URL}/export/csv/`, '_blank');
  };

  const getConfidenceBadge = (confidence) => {
    if (confidence >= 85) {
      return (
        <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-700">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
          {confidence}% High
        </span>
      );
    }
    if (confidence >= 60) {
      return (
        <span className="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2.5 py-0.5 text-xs font-semibold text-amber-700">
          <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
          {confidence}% Medium
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-rose-50 px-2.5 py-0.5 text-xs font-semibold text-rose-700">
        <span className="h-1.5 w-1.5 rounded-full bg-rose-500" />
        {confidence}% Low
      </span>
    );
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return (
          <span className="inline-flex items-center gap-1 rounded-md bg-emerald-50 px-2 py-0.5 text-xs font-medium text-emerald-700">
            <CheckCircle2 className="h-3 w-3 text-emerald-600" /> Completed
          </span>
        );
      case 'processing':
        return (
          <span className="inline-flex items-center gap-1 rounded-md bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700">
            <Clock className="h-3 w-3 animate-spin text-blue-600" /> Processing
          </span>
        );
      case 'failed':
        return (
          <span className="inline-flex items-center gap-1 rounded-md bg-red-50 px-2 py-0.5 text-xs font-medium text-red-700">
            <AlertCircle className="h-3 w-3 text-red-600" /> Failed
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 rounded-md bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700">
            Pending
          </span>
        );
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Top Banner & Quick Actions */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900 md:text-3xl">
            Document Intelligence Overview
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Real-time OCR extraction performance, classification accuracy, and audit metrics.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleExportCsv}
            className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50"
          >
            <FileSpreadsheet className="h-4 w-4 text-emerald-600" />
            <span>Export CSV</span>
          </button>
          <button
            onClick={openUpload}
            className="flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm shadow-indigo-600/30 transition hover:bg-indigo-700"
          >
            <UploadCloud className="h-4 w-4" />
            <span>Upload Document</span>
          </button>
        </div>
      </div>

      {/* Metric KPI Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {/* Total Documents */}
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Total Ingested
            </span>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
              <FileText className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-slate-900">
              {stats?.total_documents ?? 0}
            </span>
            <span className="text-xs font-semibold text-emerald-600">
              {stats?.completed_documents ?? 0} completed
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500">
            Across invoices, resumes, IDs & forms
          </p>
        </div>

        {/* Average OCR Confidence */}
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Avg OCR Confidence
            </span>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
              <Sparkles className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-slate-900">
              {stats?.average_ocr_confidence ?? 0}%
            </span>
            <span className="text-xs font-semibold text-slate-500">
              PyMuPDF + Tesseract
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500">
            Character clarity across all pages
          </p>
        </div>

        {/* Extraction Accuracy */}
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Extraction Accuracy
            </span>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
              <TrendingUp className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-slate-900">
              {stats?.accuracy_rate ?? 100}%
            </span>
            <span className="text-xs font-semibold text-slate-500">
              {stats?.total_fields_extracted ?? 0} fields
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500">
            {stats?.total_corrections ?? 0} manual corrections recorded
          </p>
        </div>

        {/* Verified Documents */}
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Human Verified
            </span>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-50 text-purple-600">
              <ShieldCheck className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-slate-900">
              {stats?.verified_documents ?? 0}
            </span>
            <span className="text-xs font-semibold text-slate-400">
              of {stats?.total_documents ?? 0} docs
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500">
            Reviewer approved & audit signed
          </p>
        </div>
      </div>

      {/* Middle row: Category Breakdown & Trend Overview */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Category Distribution */}
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm lg:col-span-1">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-slate-900">Document Categories</h2>
            <Layers className="h-4 w-4 text-slate-400" />
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Auto-classified via heuristic & regex scoring
          </p>

          <div className="mt-6 space-y-4">
            {stats?.category_distribution && stats.category_distribution.length > 0 ? (
              stats.category_distribution.map((cat) => (
                <div key={cat.category} className="space-y-1.5">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-slate-700">{cat.label}</span>
                    <span className="text-slate-500">
                      {cat.count} docs ({cat.percentage}%)
                    </span>
                  </div>
                  <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
                    <div
                      className="h-full rounded-full bg-indigo-600 transition-all duration-500"
                      style={{ width: `${cat.percentage}%` }}
                    />
                  </div>
                </div>
              ))
            ) : (
              <p className="py-6 text-center text-xs text-slate-400">
                No documents categorized yet.
              </p>
            )}
          </div>
        </div>

        {/* Processing Performance & Daily Activity */}
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm lg:col-span-2">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-slate-900">Processing Performance</h2>
              <p className="text-xs text-slate-500 mt-1">
                Average latency: ~{stats?.average_processing_time_ms ?? 0} ms per document
              </p>
            </div>
            <BarChart3 className="h-5 w-5 text-indigo-600" />
          </div>

          <div className="mt-8 flex h-48 items-end justify-between gap-3 px-2">
            {stats?.daily_trends && stats.daily_trends.length > 0 ? (
              stats.daily_trends.map((item, idx) => {
                const maxCount = Math.max(...stats.daily_trends.map((d) => d.count), 1);
                const heightPercent = Math.max(15, (item.count / maxCount) * 100);
                return (
                  <div key={idx} className="flex flex-1 flex-col items-center gap-2">
                    <div className="text-[11px] font-bold text-slate-600">{item.count}</div>
                    <div className="w-full max-w-[40px] rounded-t-lg bg-indigo-500/20 hover:bg-indigo-600 transition-all" style={{ height: `${heightPercent}%` }}>
                      <div className="h-full w-full rounded-t-lg bg-indigo-600/80 transition-all" />
                    </div>
                    <span className="text-[11px] text-slate-400">{item.date}</span>
                  </div>
                );
              })
            ) : (
              <div className="flex h-full w-full items-center justify-center text-xs text-slate-400">
                Activity data loading...
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Ingested Documents Table */}
      <div className="rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="flex items-center justify-between border-b border-slate-100 px-6 py-4">
          <div>
            <h2 className="text-base font-bold text-slate-900">Recently Ingested Documents</h2>
            <p className="text-xs text-slate-500">Click any document to inspect OCR text and correct fields</p>
          </div>
          <Link
            to="/documents"
            className="flex items-center gap-1 text-xs font-bold text-indigo-600 hover:text-indigo-700"
          >
            <span>View All</span>
            <ArrowUpRight className="h-3.5 w-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="border-b border-slate-100 bg-slate-50/50 text-[11px] font-bold uppercase tracking-wider text-slate-400">
              <tr>
                <th className="px-6 py-3.5">Document</th>
                <th className="px-6 py-3.5">Category</th>
                <th className="px-6 py-3.5">Status</th>
                <th className="px-6 py-3.5">OCR Quality</th>
                <th className="px-6 py-3.5">Verified</th>
                <th className="px-6 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {recentDocs && recentDocs.length > 0 ? (
                recentDocs.map((doc) => (
                  <tr key={doc.id} className="transition hover:bg-slate-50/80">
                    <td className="px-6 py-4">
                      <Link to={`/documents/${doc.id}`} className="flex items-center gap-3 group">
                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-600 group-hover:bg-indigo-50 group-hover:text-indigo-600 transition">
                          <FileText className="h-5 w-5" />
                        </div>
                        <div>
                          <div className="font-semibold text-slate-900 group-hover:text-indigo-600 transition">
                            {doc.title}
                          </div>
                          <div className="text-xs text-slate-400">
                            {doc.filename} • {doc.page_count} pg
                          </div>
                        </div>
                      </Link>
                    </td>
                    <td className="px-6 py-4">
                      <span className="rounded-lg bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">
                        {doc.category_display || doc.category}
                      </span>
                    </td>
                    <td className="px-6 py-4">{getStatusBadge(doc.status)}</td>
                    <td className="px-6 py-4">{getConfidenceBadge(doc.ocr_confidence)}</td>
                    <td className="px-6 py-4">
                      {doc.is_verified ? (
                        <span className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-600">
                          <CheckCircle2 className="h-3.5 w-3.5" /> Verified
                        </span>
                      ) : (
                        <span className="text-xs text-slate-400">Needs Review</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link
                        to={`/documents/${doc.id}`}
                        className="inline-flex items-center rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-indigo-600 transition hover:bg-indigo-50"
                      >
                        Review
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="py-8 text-center text-xs text-slate-400">
                    No documents uploaded yet. Click "Upload Document" to start.
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

