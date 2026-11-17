import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  FileText,
  Search,
  UploadCloud,
  LogOut,
  User,
  ShieldCheck,
  CheckCircle2,
  ExternalLink
} from 'lucide-react';

export default function Navbar({ onOpenUpload }) {
  const { user, logout, isAdmin, isReviewer } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-slate-200 bg-white/95 px-6 backdrop-blur transition-all">
      {/* Brand logo & mobile menu */}
      <div className="flex items-center gap-3">
        <Link to="/" className="flex items-center gap-2.5">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 shadow-md shadow-indigo-500/20">
            <FileText className="h-5 w-5 text-white" />
          </div>
          <div>
            <span className="text-xl font-bold tracking-tight text-slate-900">
              Docu<span className="text-indigo-600">Mind</span>
            </span>
            <span className="ml-2 hidden rounded-md bg-indigo-50 px-2 py-0.5 text-xs font-semibold text-indigo-700 sm:inline-block">
              v1.0 OCR
            </span>
          </div>
        </Link>
      </div>

      {/* Global Quick Search Bar */}
      <div className="hidden max-w-md flex-1 px-8 md:block">
        <div
          onClick={() => navigate('/search')}
          className="flex cursor-pointer items-center gap-2 rounded-xl border border-slate-200 bg-slate-50/80 px-3.5 py-2 text-sm text-slate-400 transition hover:border-slate-300 hover:bg-slate-100"
        >
          <Search className="h-4 w-4 text-slate-400" />
          <span>Search documents, extracted fields, invoices, names...</span>
          <kbd className="ml-auto rounded bg-slate-200/80 px-1.5 py-0.5 text-[10px] font-semibold text-slate-600">
            /
          </kbd>
        </div>
      </div>

      {/* Right controls: Upload button, Docs link, User dropdown */}
      <div className="flex items-center gap-3">
        {isReviewer && (
          <button
            onClick={onOpenUpload}
            className="flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm shadow-indigo-600/30 transition hover:bg-indigo-700 active:scale-[0.98]"
          >
            <UploadCloud className="h-4 w-4" />
            <span className="hidden sm:inline">Upload Document</span>
          </button>
        )}

        <a
          href="/api/docs/"
          target="_blank"
          rel="noreferrer"
          className="hidden items-center gap-1.5 rounded-xl border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 transition hover:bg-slate-50 sm:flex"
          title="Swagger / OpenAPI Documentation"
        >
          <span>API Docs</span>
          <ExternalLink className="h-3 w-3 text-slate-400" />
        </a>

        {/* User Info & Role Pill */}
        <div className="flex items-center gap-3 border-l border-slate-200 pl-3">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-100 font-bold text-slate-700">
              {user?.first_name ? user.first_name[0] : (user?.username?.[0]?.toUpperCase() || 'U')}
            </div>
            <div className="hidden text-left lg:block">
              <div className="text-xs font-bold text-slate-800">
                {user?.first_name ? `${user.first_name} ${user.last_name || ''}` : user?.username}
              </div>
              <div className="flex items-center gap-1">
                <span
                  className={`inline-block h-1.5 w-1.5 rounded-full ${
                    isAdmin
                      ? 'bg-purple-500'
                      : isReviewer
                      ? 'bg-blue-500'
                      : 'bg-emerald-500'
                  }`}
                />
                <span className="text-[11px] font-medium text-slate-500 capitalize">
                  {user?.role_display || user?.role || 'User'}
                </span>
              </div>
            </div>
          </div>

          <button
            onClick={logout}
            className="rounded-lg p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600"
            title="Log out"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </header>
  );
}
