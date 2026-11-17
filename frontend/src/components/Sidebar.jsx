import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Files,
  Search,
  History,
  FileSpreadsheet,
  CheckCircle,
  Cpu,
  Shield,
  HelpCircle
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', to: '/', icon: LayoutDashboard },
  { name: 'Documents', to: '/documents', icon: Files },
  { name: 'Search & Query', to: '/search', icon: Search },
  { name: 'Audit & History', to: '/audit', icon: History },
];

export default function Sidebar() {
  return (
    <aside className="hidden w-64 flex-col justify-between border-r border-slate-200 bg-white p-4 md:flex">
      <div className="space-y-6">
        <div className="px-2">
          <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
            Platform
          </p>
          <nav className="mt-2 space-y-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.name}
                  to={item.to}
                  className={({ isActive }) =>
                    `group flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-semibold transition ${
                      isActive
                        ? 'bg-indigo-50 text-indigo-700 shadow-sm shadow-indigo-100'
                        : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                    }`
                  }
                >
                  <Icon className="h-5 w-5 transition group-hover:scale-105" />
                  <span>{item.name}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Engine status indicator card */}
        <div className="rounded-2xl border border-slate-200/80 bg-gradient-to-b from-slate-50 to-white p-4 shadow-sm">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500"></span>
            </span>
            <span className="text-xs font-bold text-slate-800">OCR & Extraction Engine</span>
          </div>

          <div className="mt-3 space-y-1.5 text-[11px] text-slate-600">
            <div className="flex justify-between">
              <span className="text-slate-400">PDF Engine:</span>
              <span className="font-semibold text-slate-700">PyMuPDF v2.1</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Image OCR:</span>
              <span className="font-semibold text-slate-700">Tesseract v5.5</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Tasks:</span>
              <span className="font-semibold text-slate-700">Celery + Redis</span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Info */}
      <div className="border-t border-slate-100 px-2 pt-4">
        <div className="flex items-center justify-between text-[11px] text-slate-400">
          <span>DocuMind Enterprise</span>
          <span>v1.0.0</span>
        </div>
      </div>
    </aside>
  );
}

