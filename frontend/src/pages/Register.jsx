import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import InteractiveLiveWallpaper from '../components/InteractiveLiveWallpaper';
import TiltCard from '../components/TiltCard';
import {
  FileText,
  Lock,
  User as UserIcon,
  Mail,
  Building,
  AlertCircle,
  ArrowRight,
  X,
  Sparkles
} from 'lucide-react';

const GoogleIcon = () => (
  <svg className="h-5 w-5" viewBox="0 0 24 24">
    <path
      fill="#4285F4"
      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
    />
    <path
      fill="#34A853"
      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
    />
    <path
      fill="#FBBC05"
      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
    />
    <path
      fill="#EA4335"
      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
    />
  </svg>
);

export default function Register() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
    role: 'reviewer',
    organization: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [googleModalOpen, setGoogleModalOpen] = useState(false);
  const [customGoogleEmail, setCustomGoogleEmail] = useState('');

  const { register, loginWithGoogle } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.password_confirm) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);
    try {
      await register(formData);
      navigate('/');
    } catch (err) {
      console.error('Registration error:', err);
      const res = err.response?.data;
      if (res) {
        const firstErr =
          res.username?.[0] ||
          res.email?.[0] ||
          res.password?.[0] ||
          res.detail ||
          'Failed to create account.';
        setError(firstErr);
      } else {
        setError('Registration failed. Please check your credentials.');
      }
    } finally {
      setLoading(false);
    }
  };

  const executeGoogleAuth = async (email, name) => {
    setLoading(true);
    setGoogleModalOpen(false);
    try {
      await loginWithGoogle({
        email: email || 'new.user.google@gmail.com',
        name: name || 'Google User',
        avatar_url: 'https://lh3.googleusercontent.com/a/default-user',
      });
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Google signup failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center p-4 selection:bg-indigo-500 selection:text-white">
      {/* 3D Interactive Live Wallpaper */}
      <InteractiveLiveWallpaper />

      <div className="relative z-10 w-full max-w-lg space-y-6">
        <div className="text-center space-y-2">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-tr from-indigo-600 to-violet-500 shadow-xl shadow-indigo-500/30">
            <FileText className="h-7 w-7 text-white" />
          </div>
          <h2 className="text-3xl font-extrabold tracking-tight text-slate-900">
            Create your Docu<span className="text-indigo-600">Mind</span> Account
          </h2>
          <p className="text-xs text-slate-500">
            Start processing documents with automated OCR and intelligent field extraction
          </p>
        </div>

        <TiltCard maxTilt={5} scale={1.01} className="rounded-3xl">
          <div className="rounded-3xl border border-white/60 bg-white/90 p-8 shadow-2xl shadow-indigo-500/10 backdrop-blur-2xl space-y-6">
            {error && (
              <div className="flex items-center gap-2 rounded-2xl bg-rose-50 border border-rose-200/60 p-3 text-xs text-rose-700">
                <AlertCircle className="h-4 w-4 shrink-0 text-rose-500" />
                <span>{error}</span>
              </div>
            )}

            {/* Google Sign In option */}
            <div>
              <button
                type="button"
                onClick={() => setGoogleModalOpen(true)}
                disabled={loading}
                className="w-full flex items-center justify-center gap-3 rounded-2xl border border-slate-200 bg-white py-2.5 px-4 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 hover:border-slate-300 active:scale-[0.99] disabled:opacity-50"
              >
                <GoogleIcon />
                <span>Sign up with Google</span>
              </button>
            </div>

            <div className="relative flex items-center justify-center">
              <div className="w-full border-t border-slate-200" />
              <span className="absolute bg-white/90 px-3 text-xs font-semibold text-slate-400 backdrop-blur-sm">
                or register with credentials
              </span>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
                    First Name
                  </label>
                  <input
                    type="text"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleChange}
                    className="w-full rounded-xl border border-slate-200 bg-white/80 px-3.5 py-2 text-sm text-slate-800 focus:border-indigo-500 focus:outline-none"
                    placeholder="Jane"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
                    Last Name
                  </label>
                  <input
                    type="text"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleChange}
                    className="w-full rounded-xl border border-slate-200 bg-white/80 px-3.5 py-2 text-sm text-slate-800 focus:border-indigo-500 focus:outline-none"
                    placeholder="Doe"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
                  Username *
                </label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  required
                  className="w-full rounded-xl border border-slate-200 bg-white/80 px-3.5 py-2 text-sm text-slate-800 focus:border-indigo-500 focus:outline-none"
                  placeholder="janedoe"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full rounded-xl border border-slate-200 bg-white/80 px-3.5 py-2 text-sm text-slate-800 focus:border-indigo-500 focus:outline-none"
                  placeholder="jane@company.com"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
                    Role
                  </label>
                  <select
                    name="role"
                    value={formData.role}
                    onChange={handleChange}
                    className="w-full rounded-xl border border-slate-200 bg-white/80 px-3 py-2 text-sm text-slate-800 focus:border-indigo-500 focus:outline-none"
                  >
                    <option value="reviewer">Reviewer / Editor</option>
                    <option value="viewer">Viewer</option>
                    <option value="admin">Administrator</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
                    Organization
                  </label>
                  <input
                    type="text"
                    name="organization"
                    value={formData.organization}
                    onChange={handleChange}
                    className="w-full rounded-xl border border-slate-200 bg-white/80 px-3.5 py-2 text-sm text-slate-800 focus:border-indigo-500 focus:outline-none"
                    placeholder="Acme Inc."
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
                    Password *
                  </label>
                  <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                    className="w-full rounded-xl border border-slate-200 bg-white/80 px-3.5 py-2 text-sm text-slate-800 focus:border-indigo-500 focus:outline-none"
                    placeholder="••••••••"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
                    Confirm Password *
                  </label>
                  <input
                    type="password"
                    name="password_confirm"
                    value={formData.password_confirm}
                    onChange={handleChange}
                    required
                    className="w-full rounded-xl border border-slate-200 bg-white/80 px-3.5 py-2 text-sm text-slate-800 focus:border-indigo-500 focus:outline-none"
                    placeholder="••••••••"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="group relative w-full flex items-center justify-center gap-2 overflow-hidden rounded-2xl bg-gradient-to-r from-indigo-600 via-indigo-500 to-violet-600 py-3 text-sm font-bold text-white shadow-lg shadow-indigo-600/30 transition-all duration-300 hover:scale-[1.01] hover:shadow-indigo-600/40 active:scale-[0.99] disabled:opacity-50"
              >
                <span>{loading ? 'Creating Account...' : 'Register Account'}</span>
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </button>
            </form>
          </div>
        </TiltCard>

        <p className="text-center text-xs font-medium text-slate-600">
          Already have an account?{' '}
          <Link to="/login" className="font-bold text-indigo-600 hover:underline">
            Sign in
          </Link>
        </p>
      </div>

      {/* Google Account Modal */}
      {googleModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-sm animate-in fade-in">
          <div className="w-full max-w-sm rounded-3xl bg-white p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <GoogleIcon />
                <h3 className="text-sm font-bold text-slate-900">Sign in with Google</h3>
              </div>
              <button
                onClick={() => setGoogleModalOpen(false)}
                className="rounded-lg p-1 text-slate-400 hover:bg-slate-100"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <p className="text-xs text-slate-500">
              Choose a Google workspace account to sign up or connect:
            </p>

            <div className="space-y-2">
              <button
                type="button"
                onClick={() => executeGoogleAuth('alex.reviewer.google@gmail.com', 'Alex Rivera')}
                className="w-full flex items-center gap-3 rounded-2xl border border-slate-200 p-3 text-left hover:bg-indigo-50/40 hover:border-indigo-300 transition"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 font-bold text-white text-sm">
                  A
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-800">Alex Rivera</div>
                  <div className="text-[11px] text-slate-500">alex.reviewer.google@gmail.com</div>
                </div>
              </button>

              <button
                type="button"
                onClick={() => executeGoogleAuth('sarah.admin.google@gmail.com', 'Sarah Connor')}
                className="w-full flex items-center gap-3 rounded-2xl border border-slate-200 p-3 text-left hover:bg-indigo-50/40 hover:border-indigo-300 transition"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-purple-600 font-bold text-white text-sm">
                  S
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-800">Sarah Connor</div>
                  <div className="text-[11px] text-slate-500">sarah.admin.google@gmail.com</div>
                </div>
              </button>
            </div>

            <div className="pt-2 border-t border-slate-100 space-y-2">
              <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                Or enter custom Google email:
              </div>
              <div className="space-y-2">
                <input
                  type="email"
                  placeholder="yourname@gmail.com"
                  value={customGoogleEmail}
                  onChange={(e) => setCustomGoogleEmail(e.target.value)}
                  className="w-full rounded-xl border border-slate-200 px-3 py-2 text-xs text-slate-800 focus:border-indigo-500 focus:outline-none"
                />
                <button
                  type="button"
                  disabled={!customGoogleEmail}
                  onClick={() => executeGoogleAuth(customGoogleEmail, customGoogleEmail.split('@')[0])}
                  className="w-full rounded-xl bg-slate-900 py-2 text-xs font-bold text-white hover:bg-slate-800 transition disabled:opacity-40"
                >
                  Continue with this Email
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
