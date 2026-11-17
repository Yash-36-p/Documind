import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  FileText,
  Lock,
  User as UserIcon,
  AlertCircle,
  ArrowRight,
  Shield,
  CheckCircle2,
  X
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

export default function Login() {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [googleModalOpen, setGoogleModalOpen] = useState(false);
  const [customGoogleEmail, setCustomGoogleEmail] = useState('');

  const { login, loginWithGoogle } = useAuth();
  const navigate = useNavigate();

  // Clear stale tokens when arriving on login page
  useEffect(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('documind_user');
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      console.error('Login error:', err);
      setError(
        err.response?.data?.detail ||
        err.response?.data?.error ||
        err.response?.data?.non_field_errors?.[0] ||
        'Invalid username or password.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignInClick = () => {
    setError('');
    const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

    // If official Google Identity Services client is configured
    if (window.google?.accounts?.id && googleClientId) {
      window.google.accounts.id.initialize({
        client_id: googleClientId,
        callback: async (response) => {
          try {
            setLoading(true);
            await loginWithGoogle({ credential: response.credential });
            navigate('/');
          } catch (err) {
            const msg = err.response?.data?.error || 'Google sign-in verification failed.';
            setError(msg);
          } finally {
            setLoading(false);
          }
        },
      });
      window.google.accounts.id.prompt();
    } else {
      // Open the Google Authentication dialog
      setGoogleModalOpen(true);
    }
  };

  const executeGoogleAuth = async (email, name) => {
    setLoading(true);
    setGoogleModalOpen(false);
    setError('');
    try {
      await loginWithGoogle({
        email: email || 'alex.reviewer.google@gmail.com',
        name: name || 'Alex Rivera (Google)',
        avatar_url: 'https://lh3.googleusercontent.com/a/default-user',
      });
      navigate('/');
    } catch (err) {
      console.error('Google Auth Failed:', err);
      const detail =
        err.response?.data?.error ||
        err.response?.data?.detail ||
        err.message ||
        'Google sign in failed. Please try again.';
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (u, p) => {
    setUsername(u);
    setPassword(p);
  };

  return (
    <div className="flex min-h-screen bg-slate-50 items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Logo & Headline */}
        <div className="text-center space-y-2">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-tr from-indigo-600 to-violet-500 shadow-lg shadow-indigo-500/25">
            <FileText className="h-7 w-7 text-white" />
          </div>
          <h2 className="text-2xl font-extrabold tracking-tight text-slate-900">
            Sign in to Docu<span className="text-indigo-600">Mind</span>
          </h2>
          <p className="text-xs text-slate-500">
            Intelligent Document Processing & OCR Extraction Platform
          </p>
        </div>

        {/* Card */}
        <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-xl shadow-slate-200/50 space-y-6">
          {error && (
            <div className="flex items-center gap-2 rounded-xl bg-rose-50 p-3 text-xs text-rose-700">
              <AlertCircle className="h-4 w-4 shrink-0 text-rose-500" />
              <span>{error}</span>
            </div>
          )}

          {/* 1. Google Sign-in Button */}
          <div>
            <button
              type="button"
              onClick={handleGoogleSignInClick}
              disabled={loading}
              className="w-full flex items-center justify-center gap-3 rounded-2xl border border-slate-200 bg-white py-2.5 px-4 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 hover:border-slate-300 active:scale-[0.99] disabled:opacity-50"
            >
              <GoogleIcon />
              <span>Sign in with Google</span>
            </button>
          </div>

          {/* Divider */}
          <div className="relative flex items-center justify-center">
            <div className="w-full border-t border-slate-200" />
            <span className="absolute bg-white px-3 text-xs font-medium text-slate-400">
              or sign in with username
            </span>
          </div>

          {/* Standard Login Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">
                Username
              </label>
              <div className="relative">
                <UserIcon className="absolute left-3.5 top-2.5 h-4 w-4 text-slate-400" />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  placeholder="admin"
                  className="w-full rounded-xl border border-slate-200 py-2.5 pl-10 pr-4 text-sm text-slate-800 placeholder-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-100"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-2.5 h-4 w-4 text-slate-400" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="••••••••"
                  className="w-full rounded-xl border border-slate-200 py-2.5 pl-10 pr-4 text-sm text-slate-800 placeholder-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-100"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-indigo-600 py-2.5 text-sm font-bold text-white shadow-md shadow-indigo-600/30 hover:bg-indigo-700 active:scale-[0.99] transition disabled:opacity-50"
            >
              <span>{loading ? 'Authenticating...' : 'Sign In'}</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </form>

          {/* Quick Demo Accounts Selection */}
          <div className="pt-2 border-t border-slate-100 space-y-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
              Quick Demo Accounts:
            </span>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => handleQuickLogin('admin', 'admin123')}
                className={`rounded-xl border p-2 text-center text-xs transition ${
                  username === 'admin'
                    ? 'border-indigo-600 bg-indigo-50/50 text-indigo-700 font-bold'
                    : 'border-slate-200 hover:bg-slate-50 text-slate-700'
                }`}
              >
                <div className="font-bold">Admin</div>
                <div className="text-[10px] text-slate-400">admin123</div>
              </button>

              <button
                type="button"
                onClick={() => handleQuickLogin('reviewer', 'reviewer123')}
                className={`rounded-xl border p-2 text-center text-xs transition ${
                  username === 'reviewer'
                    ? 'border-indigo-600 bg-indigo-50/50 text-indigo-700 font-bold'
                    : 'border-slate-200 hover:bg-slate-50 text-slate-700'
                }`}
              >
                <div className="font-bold">Reviewer</div>
                <div className="text-[10px] text-slate-400">reviewer123</div>
              </button>

              <button
                type="button"
                onClick={() => handleQuickLogin('viewer', 'viewer123')}
                className={`rounded-xl border p-2 text-center text-xs transition ${
                  username === 'viewer'
                    ? 'border-indigo-600 bg-indigo-50/50 text-indigo-700 font-bold'
                    : 'border-slate-200 hover:bg-slate-50 text-slate-700'
                }`}
              >
                <div className="font-bold">Viewer</div>
                <div className="text-[10px] text-slate-400">viewer123</div>
              </button>
            </div>
          </div>
        </div>

        <p className="text-center text-xs text-slate-500">
          Need an account?{' '}
          <Link to="/register" className="font-bold text-indigo-600 hover:underline">
            Register here
          </Link>
        </p>
      </div>

      {/* Google Account Sign-In Modal */}
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
              Select a Google account to sign in to DocuMind:
            </p>

            {/* Google Profile Cards */}
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

            {/* Custom Google Email input */}
            <div className="pt-2 border-t border-slate-100 space-y-2">
              <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                Or enter any Google account:
              </div>
              <div className="space-y-2">
                <input
                  type="email"
                  placeholder="your.email@gmail.com"
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
