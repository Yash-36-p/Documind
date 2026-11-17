import React, { useState, useEffect } from 'react';
import api from '../api/client';
import {
  History,
  Shield,
  FileSpreadsheet,
  Filter,
  RefreshCw,
  User,
  CheckCircle2,
  AlertCircle,
  FileText,
  Clock
} from 'lucide-react';

const ACTIONS = [
  { value: '', label: 'All Actions' },
  { value: 'UPLOAD', label: 'Document Uploaded' },
  { value: 'PROCESS_SUCCESS', label: 'Processing Succeeded' },
  { value: 'PROCESS_FAIL', label: 'Processing Failed' },
  { value: 'FIELD_EDIT', label: 'Field Corrected' },
  { value: 'FIELD_CREATE', label: 'Field Created' },
  { value: 'FIELD_DELETE', label: 'Field Deleted' },
  { value: 'CLASSIFICATION_CHANGE', label: 'Classification Overridden' },
  { value: 'VERIFY', label: 'Document Verified' },
  { value: 'DELETE', label: 'Document Deleted' },
  { value: 'EXPORT', label: 'CSV Exported' },
  { value: 'LOGIN', label: 'User Login' },
];

export default function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState('');

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (actionFilter) params.append('action', actionFilter);
      const res = await api.get(`/audit/logs/?${params.toString()}`);
      setLogs(res.data.results || res.data);
    } catch (err) {
      console.error('Failed to fetch audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [actionFilter]);

  const getActionColor = (action) => {
    switch (action) {
      case 'UPLOAD':
      case 'LOGIN':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'PROCESS_SUCCESS':
      case 'VERIFY':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'FIELD_EDIT':
      case 'CLASSIFICATION_CHANGE':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'DELETE':
      case 'PROCESS_FAIL':
        return 'bg-rose-50 text-rose-700 border-rose-200';
      default:
        return 'bg-slate-50 text-slate-700 border-slate-200';
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900 md:text-3xl">
            Audit Trails & Activity Logs
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Immutable tracking for regulatory compliance, manual correction history, and user operations.
          </p>
        </div>

        <button
          onClick={fetchLogs}
          disabled={loading}
          className="flex items-center gap-1.5 self-start rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs font-bold text-slate-700 hover:bg-slate-50 transition shadow-sm"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filter toolbar */}
      <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Filter className="h-4 w-4 text-slate-400" />
          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2 text-sm font-semibold text-slate-700 focus:border-indigo-500 focus:bg-white focus:outline-none"
          >
            {ACTIONS.map((a) => (
              <option key={a.value} value={a.value}>
                {a.label}
              </option>
            ))}
          </select>
        </div>

        <span className="text-xs font-semibold text-slate-500">
          Showing {logs.length} audit entries
        </span>
      </div>

      {/* Audit Log Table */}
      <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="border-b border-slate-100 bg-slate-50/70 text-[11px] font-bold uppercase tracking-wider text-slate-400">
              <tr>
                <th className="px-6 py-3.5">Timestamp</th>
                <th className="px-6 py-3.5">Action</th>
                <th className="px-6 py-3.5">Operator</th>
                <th className="px-6 py-3.5">Target Document</th>
                <th className="px-6 py-3.5">Details & Metadata</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="5" className="py-12 text-center text-sm text-slate-400">
                    <RefreshCw className="mx-auto h-6 w-6 animate-spin text-indigo-500 mb-2" />
                    Loading audit trail...
                  </td>
                </tr>
              ) : logs && logs.length > 0 ? (
                logs.map((log) => (
                  <tr key={log.id} className="transition hover:bg-slate-50/70">
                    <td className="px-6 py-4 whitespace-nowrap text-xs text-slate-500">
                      <div className="font-semibold text-slate-700">
                        {new Date(log.timestamp).toLocaleDateString()}
                      </div>
                      <div className="text-[11px] text-slate-400">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </div>
                    </td>

                    <td className="px-6 py-4">
                      <span
                        className={`inline-block rounded-md border px-2.5 py-1 text-xs font-bold ${getActionColor(
                          log.action
                        )}`}
                      >
                        {log.action_display || log.action}
                      </span>
                    </td>

                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="flex h-7 w-7 items-center justify-center rounded-full bg-slate-100 text-xs font-bold text-slate-600">
                          {log.user_name ? log.user_name[0] : 'S'}
                        </div>
                        <div>
                          <div className="font-semibold text-slate-800 text-xs">
                            {log.user_name || 'System'}
                          </div>
                          {log.ip_address && (
                            <div className="text-[10px] text-slate-400 font-mono">
                              {log.ip_address}
                            </div>
                          )}
                        </div>
                      </div>
                    </td>

                    <td className="px-6 py-4">
                      <div className="font-semibold text-slate-800 text-xs">
                        {log.document_title || '—'}
                      </div>
                    </td>

                    <td className="px-6 py-4">
                      <div className="max-w-md overflow-hidden text-ellipsis rounded-lg bg-slate-50 p-2 text-[11px] font-mono text-slate-600">
                        {JSON.stringify(log.details)}
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className="py-12 text-center text-sm text-slate-400">
                    No activity records found matching filters.
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

