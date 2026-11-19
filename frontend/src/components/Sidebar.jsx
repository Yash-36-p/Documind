import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Files,
  Search,
  History,
  Sparkles,
  Cpu,
  Layers,
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', to: '/', icon: LayoutDashboard },
  { name: 'Documents', to: '/documents', icon: Files },
  { name: 'Search & Query', to: '/search', icon: Search },
  { name: 'Audit & History', to: '/audit', icon: History },
];

export default function Sidebar() {
  return (
    <aside className="hidden w-64 flex-col justify-between border-r border-slate-200/70 bg-white/70 p-4 backdrop-blur-xl md:flex">
      <div className="space-y-6">
        <div className="px-2">
          <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
            Platform Navigation
          </p>
          <nav className="mt-2 space-y-1.5">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.name}
                  to={item.to}
                  className={({ isActive }) =>
                    `group relative flex items-center gap-3 overflow-hidden rounded-xl px-3.5 py-2.5 text-sm font-semibold transition-all duration-200 ${
                      isActive
                        ? 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-md shadow-indigo-500/25 scale-[1.02]'
                        : 'text-slate-600 hover:bg-white hover:text-slate-900 hover:shadow-sm hover:scale-[1.01]'
                    }`
                  }
                >
                  <Icon className="h-5 w-5 transition-transform duration-300 group-hover:scale-110" />
                  <span>{item.name}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* 3D Holographic Engine Status Card */}
        <div className="relative overflow-hidden rounded-2xl border border-indigo-100/80 bg-gradient-to-b from-white/90 to-indigo-50/50 p-4 shadow-sm backdrop-blur-md">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500"></span>
            </span>
            <span className="text-xs font-bold text-slate-800">3D Neural OCR Engine</span>
          </div>

          <div className="mt-3 space-y-2 text-[11px] text-slate-600">
            <div className="flex items-center justify-between border-b border-indigo-100/50 pb-1.5">
              <span className="text-slate-500">PDF Extraction:</span>
              <span className="font-semibold text-indigo-700">PyMuPDF v2.1</span>
            </div>
            <div className="flex items-center justify-between border-b border-indigo-100/50 pb-1.5">
              <span className="text-slate-500">Optical OCR:</span>
              <span className="font-semibold text-violet-700">Tesseract v5.5</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-500">Visual Mode:</span>
              <span className="flex items-center gap-1 font-semibold text-emerald-600">
                <Sparkles className="h-3 w-3" />
                Live 3D Active
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Info */}
      <div className="border-t border-slate-200/60 px-2 pt-4">
        <div className="flex items-center justify-between text-[11px] text-slate-400 font-medium">
          <span>DocuMind Enterprise</span>
          <span className="rounded bg-slate-100 px-1.5 py-0.5 text-slate-500">v1.0 3D</span>
        </div>
      </div>
    </aside>
  );
}
