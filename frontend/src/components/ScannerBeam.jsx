import React, { useState } from 'react';
import { Scan, Zap, Pause, Play } from 'lucide-react';

export default function ScannerBeam({ active = true, label = 'AI OCR Neural Scanner' }) {
  const [isScanning, setIsScanning] = useState(active);

  if (!isScanning) {
    return (
      <button
        onClick={() => setIsScanning(true)}
        className="absolute top-3 right-3 z-30 flex items-center gap-1.5 rounded-full bg-slate-900/80 px-2.5 py-1 text-[11px] font-medium text-cyan-400 backdrop-blur-md transition-all hover:bg-slate-900"
      >
        <Play className="h-3 w-3" />
        <span>Resume 3D Scan</span>
      </button>
    );
  }

  return (
    <div className="pointer-events-none absolute inset-0 z-20 overflow-hidden rounded-[inherit]">
      {/* Laser Scanning Line */}
      <div className="animate-laser-sweep absolute left-0 right-0 h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent shadow-[0_0_15px_#22d3ee]">
        {/* Glow Aura */}
        <div className="absolute -top-3 left-0 right-0 h-7 bg-cyan-400/15 blur-sm" />
        
        {/* Trailing scan gradient */}
        <div className="absolute top-1 left-0 right-0 h-16 bg-gradient-to-b from-cyan-500/10 to-transparent pointer-events-none" />

        {/* Central HUD Target Node */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center gap-1 rounded-full bg-cyan-500/90 px-2 py-0.5 text-[9px] font-bold tracking-wider text-slate-950 uppercase shadow-lg shadow-cyan-500/50">
          <Zap className="h-2.5 w-2.5 fill-current" />
          <span>OCR PASS</span>
        </div>
      </div>

      {/* Futuristic HUD Corner Crosshairs */}
      <div className="absolute top-3 left-3 h-4 w-4 border-t-2 border-l-2 border-cyan-400/70" />
      <div className="absolute top-3 right-3 h-4 w-4 border-t-2 border-r-2 border-cyan-400/70" />
      <div className="absolute bottom-3 left-3 h-4 w-4 border-b-2 border-l-2 border-cyan-400/70" />
      <div className="absolute bottom-3 right-3 h-4 w-4 border-b-2 border-r-2 border-cyan-400/70" />

      {/* Scan Status Badge (Interactive) */}
      <div className="pointer-events-auto absolute top-3 right-3 z-30 flex items-center gap-1.5 rounded-full bg-slate-950/80 px-2.5 py-1 text-[10px] font-semibold tracking-wide text-cyan-300 backdrop-blur-md border border-cyan-500/30 shadow-lg">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
        </span>
        <span>{label}</span>
        <button
          onClick={() => setIsScanning(false)}
          className="ml-1 rounded p-0.5 hover:bg-white/10"
          title="Pause Scan Beam"
        >
          <Pause className="h-2.5 w-2.5" />
        </button>
      </div>
    </div>
  );
}
