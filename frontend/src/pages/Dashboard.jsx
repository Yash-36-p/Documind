import React, { useState, useEffect } from 'react';
import { Link, useOutletContext } from 'react-router-dom';
import api, { API_BASE_URL } from '../api/client';
import TiltCard from '../components/TiltCard';
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
  Layers,
  Zap,
  Activity
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
        <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50/90 border border-emerald-200/60 px-2.5 py-0.5 text-xs font-semibold text-emerald-700 shadow-sm">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
          {confidence}% High
        </span>
      );
    }
    if (confidence >= 60) {
      return (
        <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-50/90 border border-amber-200/60 px-2.5 py-0.5 text-xs font-semibold text-amber-700 shadow-sm">
          <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
          {confidence}% Med
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-rose-50/90 border border-rose-200/60 px-2.5 py-0.5 text-xs font-semibold text-rose-700 shadow-sm">
        <span className="h-1.5 w-1.5 rounded-full bg-rose-500" />
        {confidence}% Low
      </span>
    );
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return (
          <span className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-50/90 border border-emerald-200/60 px-2.5 py-0.5 text-xs font-semibold text-emerald-700 shadow-sm">
            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" /> Completed
          </span>
        );
      case 'processing':
        return (
          <span className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-50/90 border border-indigo-200/60 px-2.5 py-0.5 text-xs font-semibold text-indigo-700 shadow-sm">
            <Clock className="h-3.5 w-3.5 animate-spin text-indigo-600" /> Neural OCR
          </span>
        );
      case 'failed':
        return (
          <span className="inline-flex items-center gap-1.5 rounded-lg bg-rose-50/90 border border-rose-200/60 px-2.5 py-0.5 text-xs font-semibold text-rose-700 shadow-sm">
            <AlertCircle className="h-3.5 w-3.5 text-rose-600" /> Failed
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 rounded-lg bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-700">
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
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-600 text-white shadow-md shadow-indigo-500/30">
              <Activity className="h-4 w-4" />
            </div>
            <h1 className="text-2xl font-black tracking-tight text-slate-900 md:text-3xl">
              Document Intelligence Overview
            </h1>
          </div>
          <p className="mt-1 text-sm text-slate-500">
            Real-time neural OCR extraction, classification accuracy, and live 3D audit telemetry.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleExportCsv}
            className="group flex items-center gap-2 rounded-2xl border border-slate-200/80 bg-white/80 px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm backdrop-blur-md transition-all hover:border-emerald-300 hover:bg-white hover:shadow-md hover:scale-[1.02] active:scale-[0.98]"
          >
            <FileSpreadsheet className="h-4 w-4 text-emerald-600 transition-transform group-hover:scale-110" />
            <span>Export CSV</span>
          </button>
          <button
            onClick={openUpload}
            className="group relative flex items-center gap-2 overflow-hidden rounded-2xl bg-gradient-to-r from-indigo-600 via-indigo-500 to-violet-600 px-5 py-2.5 text-sm font-bold text-white shadow-lg shadow-indigo-600/30 transition-all duration-300 hover:scale-[1.03] hover:shadow-indigo-600/40 active:scale-[0.98]"
          >
            <div className="animate-shine pointer-events-none absolute inset-0 w-1/2 bg-white/25" />
            <UploadCloud className="h-4 w-4 transition-transform group-hover:-translate-y-0.5" />
            <span>Upload Document</span>
          </button>
        </div>
      </div>

      {/* 3D Physics Tilt KPI Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {/* Total Documents */}
        <TiltCard maxTilt={8} scale={1.03}>
          <div className="h-full rounded-3xl border border-white/60 bg-white/85 p-6 shadow-xl shadow-indigo-500/5 backdrop-blur-xl transition-all hover:border-indigo-300/80">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Total Ingested
              </span>
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-indigo-500 to-violet-500 text-white shadow-md shadow-indigo-500/25">
                <FileText className="h-6 w-6" />
              </div>
            </div>
            <div className="mt-4 flex items-baseline gap-2">
              <span className="text-3xl font-black text-slate-900">
                {stats?.total_documents ?? 0}
              </span>
              <span className="text-xs font-bold text-emerald-600">
                {stats?.completed_documents ?? 0} completed
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-500">
              Across invoices, resumes, IDs & certificates
            </p>
          </div>
        </TiltCard>

        {/* Average OCR Confidence */}
        <TiltCard maxTilt={8} scale={1.03}>
          <div className="h-full rounded-3xl border border-white/60 bg-white/85 p-6 shadow-xl shadow-emerald-500/5 backdrop-blur-xl transition-all hover:border-emerald-300/80">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Avg OCR Confidence
              </span>
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-emerald-500 to-teal-500 text-white shadow-md shadow-emerald-500/25">
                <Sparkles className="h-6 w-6" />
              </div>
            </div>
            <div className="mt-4 flex items-baseline gap-2">
              <span className="text-3xl font-black text-slate-900">
                {stats?.average_ocr_confidence ?? 0}%
              </span>
              <span className="text-xs font-bold text-slate-500">
                Neural PyMuPDF + OCR
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-500">
              Estimated character clarity and fidelity
            </p>
          </div>
        </TiltCard>

        {/* Extraction Accuracy */}
        <TiltCard maxTilt={8} scale={1.03}>
          <div className="h-full rounded-3xl border border-white/60 bg-white/85 p-6 shadow-xl shadow-blue-500/5 backdrop-blur-xl transition-all hover:border-blue-300/80">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Extraction Accuracy
              </span>
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-blue-500 to-cyan-500 text-white shadow-md shadow-blue-500/25">
                <TrendingUp className="h-6 w-6" />
              </div>
            </div>
            <div className="mt-4 flex items-baseline gap-2">
              <span className="text-3xl font-black text-slate-900">
                {stats?.accuracy_rate ?? 100}%
              </span>
              <span className="text-xs font-bold text-indigo-600">
                {stats?.total_fields_extracted ?? 0} fields
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-500">
              {stats?.total_corrections ?? 0} verified field updates
            </p>
          </div>
        </TiltCard>

        {/* Verified Documents */}
        <TiltCard maxTilt={8} scale={1.03}>
          <div className="h-full rounded-3xl border border-white/60 bg-white/85 p-6 shadow-xl shadow-purple-500/5 backdrop-blur-xl transition-all hover:border-purple-300/80">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Human Verified
              </span>
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-purple-500 to-pink-500 text-white shadow-md shadow-purple-500/25">
                <ShieldCheck className="h-6 w-6" />
              </div>
            </div>
            <div className="mt-4 flex items-baseline gap-2">
              <span className="text-3xl font-black text-slate-900">
                {stats?.verified_documents ?? 0}
              </span>
              <span className="text-xs font-bold text-slate-400">
                of {stats?.total_documents ?? 0} docs
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-500">
              Reviewer approved & audit signed
            </p>
          </div>
        </TiltCard>
      </div>

      {/* Middle row: Category Breakdown & Trend Overview */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Category Distribution */}
        <div className="rounded-3xl border border-white/60 bg-white/85 p-6 shadow-xl shadow-indigo-500/5 backdrop-blur-xl lg:col-span-1 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-slate-900">Document Categories</h2>
              <p className="text-xs text-slate-500">
                Multi-feature scoring & pattern classification
              </p>
            </div>
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
              <Layers className="h-4 w-4" />
            </div>
          </div>

          <div className="space-y-4 pt-2">
            {stats?.category_distribution && stats.category_distribution.length > 0 ? (
              stats.category_distribution.map((cat) => (
                <div key={cat.category} className="group space-y-1.5">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-slate-700 group-hover:text-indigo-600 transition">
                      {cat.label}
                    </span>
                    <span className="text-slate-500 font-mono">
                      {cat.count} ({cat.percentage}%)
                    </span>
                  </div>
                  <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 transition-all duration-700 group-hover:shadow-[0_0_8px_#6366f1]"
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
        <div className="rounded-3xl border border-white/60 bg-white/85 p-6 shadow-xl shadow-indigo-500/5 backdrop-blur-xl lg:col-span-2">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-slate-900">Processing Performance & Latency</h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Average ingestion speed: ~{stats?.average_processing_time_ms ?? 0} ms per document
              </p>
            </div>
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-violet-50 text-violet-600">
              <BarChart3 className="h-4 w-4" />
            </div>
          </div>

          <div className="mt-8 flex h-48 items-end justify-between gap-3 px-2">
            {stats?.daily_trends && stats.daily_trends.length > 0 ? (
              stats.daily_trends.map((item, idx) => {
                const maxCount = Math.max(...stats.daily_trends.map((d) => d.count), 1);
                const heightPercent = Math.max(15, (item.count / maxCount) * 100);
                return (
                  <div key={idx} className="group flex flex-1 flex-col items-center gap-2">
                    <div className="text-[11px] font-bold text-slate-600 group-hover:text-indigo-600 transition">
                      {item.count}
                    </div>
                    <div
                      className="w-full max-w-[44px] rounded-t-xl bg-slate-100 transition-all duration-300 group-hover:bg-indigo-100"
                      style={{ height: `${heightPercent}%` }}
                    >
                      <div className="h-full w-full rounded-t-xl bg-gradient-to-t from-indigo-600 via-indigo-500 to-violet-500 transition-all duration-500 group-hover:shadow-[0_0_12px_#6366f1]" />
                    </div>
                    <span className="text-[10px] font-semibold text-slate-400">{item.date}</span>
                  </div>
                );
              })
            ) : (
              <div className="flex h-full w-full items-center justify-center text-xs text-slate-400">
                Activity telemetry initializing...
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Ingested Documents Table */}
      <div className="rounded-3xl border border-white/60 bg-white/85 shadow-xl shadow-indigo-500/5 backdrop-blur-xl overflow-hidden">
        <div className="flex items-center justify-between border-b border-slate-100 px-6 py-5">
          <div>
            <h2 className="text-base font-bold text-slate-900">Recently Ingested Documents</h2>
            <p className="text-xs text-slate-500">Click any document to inspect OCR text and correct fields</p>
          </div>
          <Link
            to="/documents"
            className="flex items-center gap-1.5 rounded-xl border border-indigo-200/80 bg-indigo-50/50 px-3.5 py-1.5 text-xs font-bold text-indigo-700 transition hover:bg-indigo-100 hover:scale-105 active:scale-95"
          >
            <span>View All Documents</span>
            <ArrowUpRight className="h-3.5 w-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="border-b border-slate-100 bg-slate-50/60 text-[11px] font-bold uppercase tracking-wider text-slate-400">
              <tr>
                <th className="px-6 py-3.5">Document</th>
                <th className="px-6 py-3.5">Category</th>
                <th className="px-6 py-3.5">Status</th>
                <th className="px-6 py-3.5">OCR Quality</th>
                <th className="px-6 py-3.5">Verified</th>
                <th className="px-6 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100/80">
              {recentDocs && recentDocs.length > 0 ? (
                recentDocs.map((doc) => (
                  <tr key={doc.id} className="group transition-all duration-200 hover:bg-indigo-50/30">
                    <td className="px-6 py-4">
                      <Link to={`/documents/${doc.id}`} className="flex items-center gap-3">
                        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-tr from-slate-100 to-indigo-50/60 text-slate-600 group-hover:from-indigo-600 group-hover:to-violet-600 group-hover:text-white group-hover:shadow-md group-hover:shadow-indigo-500/30 transition-all duration-300">
                          <FileText className="h-5 w-5" />
                        </div>
                        <div>
                          <div className="font-bold text-slate-900 group-hover:text-indigo-600 transition">
                            {doc.title}
                          </div>
                          <div className="text-xs text-slate-400">
                            {doc.filename} • {doc.page_count} {doc.page_count === 1 ? 'page' : 'pages'}
                          </div>
                        </div>
                      </Link>
                    </td>
                    <td className="px-6 py-4">
                      <span className="rounded-xl border border-slate-200/80 bg-white/80 px-2.5 py-1 text-xs font-semibold text-slate-700 shadow-sm">
                        {doc.category_display || doc.category}
                      </span>
                    </td>
                    <td className="px-6 py-4">{getStatusBadge(doc.status)}</td>
                    <td className="px-6 py-4">{getConfidenceBadge(doc.ocr_confidence)}</td>
                    <td className="px-6 py-4">
                      {doc.is_verified ? (
                        <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-bold text-emerald-700 border border-emerald-200/60">
                          <CheckCircle2 className="h-3.5 w-3.5" /> Verified
                        </span>
                      ) : (
                        <span className="text-xs font-medium text-slate-400">Needs Review</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link
                        to={`/documents/${doc.id}`}
                        className="inline-flex items-center rounded-xl bg-slate-900 px-3.5 py-1.5 text-xs font-bold text-white shadow-sm transition-all hover:bg-indigo-600 hover:shadow-md hover:scale-105 active:scale-95"
                      >
                        Inspect 3D
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="py-8 text-center text-xs text-slate-400">
                    No documents uploaded yet. Click "Upload Document" to begin.
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
