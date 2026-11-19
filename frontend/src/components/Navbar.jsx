import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  FileText,
  Search,
  UploadCloud,
  LogOut,
  ExternalLink,
  Sparkles
} from 'lucide-react';

export default function Navbar({ onOpenUpload }) {
  const { user, logout, isAdmin, isReviewer } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-slate-200/70 bg-white/80 px-6 backdrop-blur-xl transition-all shadow-sm">
      {/* Brand logo & 3D glowing badge */}
      <div className="flex items-center gap-3">
        <Link to="/" className="group flex items-center gap-2.5">
          <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-violet-500 shadow-md shadow-indigo-500/25 transition-all duration-300 group-hover:scale-105 group-hover:shadow-indigo-500/40">
            <FileText className="h-5 w-5 text-white transition-transform group-hover:rotate-6" />
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500 border border-white"></span>
            </span>
          </div>
          <div>
            <span className="text-xl font-bold tracking-tight text-slate-900">
              Docu<span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600">Mind</span>
            </span>
            <span className="ml-2 hidden rounded-full border border-indigo-200 bg-indigo-50/80 px-2 py-0.5 text-[11px] font-bold text-indigo-700 backdrop-blur-sm sm:inline-block">
              3D Intelligent IDP
            </span>
          </div>
        </Link>
      </div>

      {/* Global Quick Search Bar */}
      <div className="hidden max-w-md flex-1 px-8 md:block">
        <div
          onClick={() => navigate('/search')}
          className="group flex cursor-pointer items-center gap-2 rounded-xl border border-slate-200/80 bg-white/70 px-3.5 py-2 text-sm text-slate-400 backdrop-blur-md transition-all hover:border-indigo-300 hover:bg-white hover:shadow-md hover:shadow-indigo-500/5"
        >
          <Search className="h-4 w-4 text-slate-400 transition-colors group-hover:text-indigo-600" />
          <span className="truncate">Search documents, extracted fields, invoices, names...</span>
          <kbd className="ml-auto rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-semibold text-slate-500 border border-slate-200">
            /
          </kbd>
        </div>
      </div>

      {/* Right controls: Upload button, Docs link, User dropdown */}
      <div className="flex items-center gap-3">
        {isReviewer && (
          <button
            onClick={onOpenUpload}
            className="group relative flex items-center gap-2 overflow-hidden rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 px-4 py-2 text-sm font-semibold text-white shadow-md shadow-indigo-500/25 transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-indigo-500/35 active:scale-95"
          >
            <div className="animate-shine pointer-events-none absolute inset-0 w-1/2 bg-white/20" />
            <UploadCloud className="h-4 w-4 transition-transform group-hover:-translate-y-0.5" />
            <span className="hidden sm:inline">Upload Document</span>
          </button>
        )}

        <a
          href="/api/docs/"
          target="_blank"
          rel="noreferrer"
          className="hidden items-center gap-1.5 rounded-xl border border-slate-200/80 bg-white/60 px-3 py-2 text-xs font-semibold text-slate-600 backdrop-blur-md transition hover:bg-white hover:text-indigo-600 sm:flex"
          title="Swagger / OpenAPI Documentation"
        >
          <span>API Docs</span>
          <ExternalLink className="h-3 w-3 text-slate-400" />
        </a>

        {/* User Info & Role Pill */}
        <div className="flex items-center gap-3 border-l border-slate-200/80 pl-3">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-slate-100 to-indigo-50 font-bold text-indigo-700 shadow-sm border border-slate-200/70">
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
                      ? 'bg-purple-500 ring-2 ring-purple-200'
                      : isReviewer
                      ? 'bg-blue-500 ring-2 ring-blue-200'
                      : 'bg-emerald-500 ring-2 ring-emerald-200'
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
            className="rounded-xl p-2 text-slate-400 transition hover:bg-rose-50 hover:text-rose-600"
            title="Log out"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </header>
  );
}
