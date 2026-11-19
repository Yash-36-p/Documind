import React, { useEffect, useRef, useState } from 'react';
import { Sparkles, Eye, EyeOff, Palette, Sliders } from 'lucide-react';

const THEMES = {
  quantum: {
    name: 'Quantum Cyan',
    nodeColor: 'rgba(56, 189, 248, 0.85)',
    lineColor: 'rgba(99, 102, 241, 0.18)',
    glowColor: 'rgba(56, 189, 248, 0.35)',
    cubeColor: 'rgba(129, 140, 248, 0.25)',
    bgGradient: 'radial-gradient(ellipse at 50% 0%, rgba(99, 102, 241, 0.12) 0%, transparent 70%)',
  },
  neonViolet: {
    name: 'Neon Violet',
    nodeColor: 'rgba(168, 85, 247, 0.85)',
    lineColor: 'rgba(236, 72, 153, 0.18)',
    glowColor: 'rgba(168, 85, 247, 0.35)',
    cubeColor: 'rgba(244, 114, 182, 0.25)',
    bgGradient: 'radial-gradient(ellipse at 50% 0%, rgba(168, 85, 247, 0.12) 0%, transparent 70%)',
  },
  emeraldMatrix: {
    name: 'Emerald Matrix',
    nodeColor: 'rgba(52, 211, 153, 0.85)',
    lineColor: 'rgba(16, 185, 129, 0.18)',
    glowColor: 'rgba(52, 211, 153, 0.35)',
    cubeColor: 'rgba(5, 150, 105, 0.25)',
    bgGradient: 'radial-gradient(ellipse at 50% 0%, rgba(16, 185, 129, 0.12) 0%, transparent 70%)',
  },
};

export default function InteractiveLiveWallpaper() {
  const canvasRef = useRef(null);
  const [isEnabled, setIsEnabled] = useState(() => {
    return localStorage.getItem('documind_live_wallpaper') !== 'false';
  });
  const [themeKey, setThemeKey] = useState(() => {
    return localStorage.getItem('documind_wallpaper_theme') || 'quantum';
  });
  const [showControls, setShowControls] = useState(false);

  const theme = THEMES[themeKey] || THEMES.quantum;

  useEffect(() => {
    localStorage.setItem('documind_live_wallpaper', isEnabled ? 'true' : 'false');
  }, [isEnabled]);

  useEffect(() => {
    localStorage.setItem('documind_wallpaper_theme', themeKey);
  }, [themeKey]);

  useEffect(() => {
    if (!isEnabled) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', handleResize);

    // Mouse coordinates with smooth damping
    const mouse = {
      x: width / 2,
      y: height / 2,
      targetX: width / 2,
      targetY: height / 2,
      radius: 140,
    };

    const handleMouseMove = (e) => {
      mouse.targetX = e.clientX;
      mouse.targetY = e.clientY;
    };
    window.addEventListener('mousemove', handleMouseMove);

    // Particles system
    const particleCount = Math.min(Math.floor((width * height) / 18000), 75);
    const particles = [];
    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.7,
        vy: (Math.random() - 0.5) * 0.7,
        radius: Math.random() * 2 + 1.2,
        baseAlpha: Math.random() * 0.6 + 0.2,
      });
    }

    // 3D Floating Isometric Document Wireframe Polyhedra
    const floatingDocs = [
      { x: width * 0.15, y: height * 0.35, z: 0, rx: 0.3, ry: 0.5, rz: 0.1, speed: 0.003, size: 55 },
      { x: width * 0.85, y: height * 0.25, z: 0, rx: -0.2, ry: 0.4, rz: -0.2, speed: 0.0025, size: 65 },
      { x: width * 0.78, y: height * 0.75, z: 0, rx: 0.4, ry: -0.3, rz: 0.3, speed: 0.0035, size: 50 },
      { x: width * 0.12, y: height * 0.78, z: 0, rx: -0.3, ry: -0.4, rz: 0.1, speed: 0.002, size: 45 },
    ];

    const render3DDocument = (doc) => {
      // Perspective projection of a 3D rectangular document with pages
      doc.ry += doc.speed;
      doc.rx += doc.speed * 0.6;

      const cosY = Math.cos(doc.ry);
      const sinY = Math.sin(doc.ry);
      const cosX = Math.cos(doc.rx);
      const sinX = Math.sin(doc.rx);

      // Mouse influence on 3D tilt
      const dx = (mouse.x - doc.x) * 0.0001;
      const dy = (mouse.y - doc.y) * 0.0001;

      // 8 Vertices of a thin 3D document sheet
      const w = doc.size;
      const h = doc.size * 1.35;
      const d = 4;

      const baseVertices = [
        [-w / 2, -h / 2, -d],
        [w / 2, -h / 2, -d],
        [w / 2, h / 2, -d],
        [-w / 2, h / 2, -d],
        [-w / 2, -h / 2, d],
        [w / 2, -h / 2, d],
        [w / 2, h / 2, d],
        [-w / 2, h / 2, d],
      ];

      const projected = baseVertices.map(([vx, vy, vz]) => {
        // Rotate around Y
        let x1 = vx * (cosY + dx) - vz * sinY;
        let z1 = vz * (cosY + dx) + vx * sinY;
        // Rotate around X
        let y1 = vy * (cosX + dy) - z1 * sinX;
        let z2 = z1 * (cosX + dy) + vy * sinX;

        // Project to 2D
        const fov = 350;
        const scale = fov / (fov + z2 + 100);
        return {
          x: doc.x + x1 * scale,
          y: doc.y + y1 * scale,
          z: z2,
        };
      });

      // Draw wireframe faces
      ctx.strokeStyle = theme.cubeColor;
      ctx.lineWidth = 1.2;

      // Front Face
      ctx.beginPath();
      ctx.moveTo(projected[0].x, projected[0].y);
      ctx.lineTo(projected[1].x, projected[1].y);
      ctx.lineTo(projected[2].x, projected[2].y);
      ctx.lineTo(projected[3].x, projected[3].y);
      ctx.closePath();
      ctx.fillStyle = theme.cubeColor.replace('0.25', '0.04');
      ctx.fill();
      ctx.stroke();

      // Horizontal lines on the document (simulating extracted text lines)
      for (let step = 0.25; step <= 0.75; step += 0.25) {
        const lx1 = projected[0].x + (projected[3].x - projected[0].x) * step + (projected[1].x - projected[0].x) * 0.15;
        const ly1 = projected[0].y + (projected[3].y - projected[0].y) * step + (projected[1].y - projected[0].y) * 0.15;
        const lx2 = projected[0].x + (projected[3].x - projected[0].x) * step + (projected[1].x - projected[0].x) * 0.85;
        const ly2 = projected[0].y + (projected[3].y - projected[0].y) * step + (projected[1].y - projected[0].y) * 0.85;
        ctx.beginPath();
        ctx.moveTo(lx1, ly1);
        ctx.lineTo(lx2, ly2);
        ctx.strokeStyle = theme.lineColor;
        ctx.stroke();
      }

      // Connecting edges to back face
      for (let i = 0; i < 4; i++) {
        ctx.beginPath();
        ctx.moveTo(projected[i].x, projected[i].y);
        ctx.lineTo(projected[i + 4].x, projected[i + 4].y);
        ctx.strokeStyle = theme.lineColor;
        ctx.stroke();
      }
    };

    // Main animation loop
    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // Smooth mouse damping
      mouse.x += (mouse.targetX - mouse.x) * 0.08;
      mouse.y += (mouse.targetY - mouse.y) * 0.08;

      // Draw floating 3D documents
      floatingDocs.forEach(render3DDocument);

      // Update and draw particles
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];

        // Move
        p.x += p.vx;
        p.y += p.vy;

        // Bounce boundaries
        if (p.x < 0 || p.x > width) p.vx *= -1;
        if (p.y < 0 || p.y > height) p.vy *= -1;

        // Interactive mouse interaction (repulsion & elastic spring)
        const dx = mouse.x - p.x;
        const dy = mouse.y - p.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < mouse.radius) {
          const force = (1 - dist / mouse.radius) * 1.5;
          p.x -= (dx / dist) * force * 1.8;
          p.y -= (dy / dist) * force * 1.8;
        }

        // Draw particle node
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = theme.nodeColor;
        ctx.shadowColor = theme.glowColor;
        ctx.shadowBlur = 6;
        ctx.fill();
        ctx.shadowBlur = 0;

        // Connect with neighboring particles
        for (let j = i + 1; j < particles.length; j++) {
          const p2 = particles[j];
          const cdx = p.x - p2.x;
          const cdy = p.y - p2.y;
          const cdist = Math.sqrt(cdx * cdx + cdy * cdy);

          if (cdist < 125) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            const lineAlpha = (1 - cdist / 125) * 0.22;
            ctx.strokeStyle = theme.lineColor.replace(/[\d\.]+\)$/, `${lineAlpha})`);
            ctx.lineWidth = 0.9;
            ctx.stroke();
          }
        }

        // Draw connection to mouse pointer if nearby
        if (dist < mouse.radius * 0.8) {
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(mouse.x, mouse.y);
          const mouseLineAlpha = (1 - dist / (mouse.radius * 0.8)) * 0.28;
          ctx.strokeStyle = theme.nodeColor.replace(/[\d\.]+\)$/, `${mouseLineAlpha})`);
          ctx.lineWidth = 1;
          ctx.stroke();
        }
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
      cancelAnimationFrame(animationFrameId);
    };
  }, [isEnabled, themeKey]);

  return (
    <>
      {/* Dynamic Canvas Background */}
      {isEnabled && (
        <div
          className="pointer-events-none fixed inset-0 z-0 overflow-hidden transition-opacity duration-700"
          style={{ background: theme.bgGradient }}
        >
          <canvas ref={canvasRef} className="absolute inset-0 h-full w-full opacity-70" />
          <div className="cyber-grid pointer-events-none absolute inset-0 opacity-40" />
        </div>
      )}

      {/* Floating 3D / Live Wallpaper Controls Floating Island (Bottom-Right) */}
      <div className="fixed bottom-4 right-4 z-40 flex items-center gap-2">
        {showControls && (
          <div className="flex items-center gap-2 rounded-2xl border border-indigo-100 bg-white/90 p-2 shadow-2xl backdrop-blur-xl transition-all animate-in fade-in slide-in-from-bottom-2">
            <span className="px-2 text-xs font-semibold text-slate-500">Theme:</span>
            {Object.entries(THEMES).map(([key, t]) => (
              <button
                key={key}
                onClick={() => setThemeKey(key)}
                className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-medium transition-all ${
                  themeKey === key
                    ? 'bg-indigo-600 text-white shadow-sm ring-2 ring-indigo-300'
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                <span
                  className="h-2 w-2 rounded-full"
                  style={{ backgroundColor: t.nodeColor }}
                />
                {t.name}
              </button>
            ))}
            <div className="h-4 w-px bg-slate-200" />
          </div>
        )}

        <button
          onClick={() => setShowControls((prev) => !prev)}
          title="Wallpaper Themes"
          className="flex h-10 w-10 items-center justify-center rounded-2xl border border-indigo-200/80 bg-white/90 text-indigo-600 shadow-lg backdrop-blur-md transition-all hover:scale-105 hover:bg-indigo-50 active:scale-95"
        >
          <Palette className="h-4 w-4" />
        </button>

        <button
          onClick={() => setIsEnabled((prev) => !prev)}
          title={isEnabled ? 'Pause 3D Live Wallpaper' : 'Activate 3D Live Wallpaper'}
          className={`flex h-10 items-center gap-2 rounded-2xl border px-3 text-xs font-semibold shadow-lg backdrop-blur-md transition-all hover:scale-105 active:scale-95 ${
            isEnabled
              ? 'border-indigo-300 bg-indigo-600 text-white shadow-indigo-200'
              : 'border-slate-300 bg-white/90 text-slate-600 hover:bg-slate-50'
          }`}
        >
          <Sparkles className={`h-3.5 w-3.5 ${isEnabled ? 'animate-spin' : ''}`} style={{ animationDuration: '6s' }} />
          <span>{isEnabled ? '3D Live' : 'Static'}</span>
          {isEnabled ? <Eye className="h-3 w-3" /> : <EyeOff className="h-3 w-3" />}
        </button>
      </div>
    </>
  );
}
