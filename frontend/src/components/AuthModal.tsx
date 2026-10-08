import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../lib/api';
import type { TokenResponse } from '../types/api';
import {
  Mail,
  Lock,
  User as UserIcon,
  Eye,
  EyeOff,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Cpu,
  Layers,
  Loader2,
} from 'lucide-react';

export const AuthModal: React.FC = () => {
  const { login } = useAuth();
  const [isLogin, setIsLogin] = useState(false);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [agreedToTerms, setAgreedToTerms] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeSlide, setActiveSlide] = useState(0);

  const heroSlides = [
    {
      title: 'Autonomous Code Synthesis',
      description: 'LangGraph multi-step state machines orchestrating isolated AST code generation and repair.',
      tag: 'AST Visualization Engine',
    },
    {
      title: 'Docker Sandbox Telemetry',
      description: 'Safe execution environments measuring runtime stdout, stderr, and precise token expenditure.',
      tag: 'Secure Execution',
    },
    {
      title: 'PostgreSQL JSONB Telemetry',
      description: 'Persistent hierarchical session graphs cached and rendered seamlessly via React Flow.',
      tag: 'State Persistence',
    },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!isLogin && !agreedToTerms) {
      setError('Please accept the Terms & Conditions to create an account.');
      return;
    }

    setLoading(true);

    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/signup';
      const payload = isLogin ? { email, password } : { email, username, password };
      const res = await api.post<TokenResponse>(endpoint, payload);
      login(res.data.access_token, res.data.user);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Authentication failed. Please verify your credentials and try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen w-screen items-center justify-center bg-[#1A0413] p-4 sm:p-6 md:p-10 selection:bg-[#871658] selection:text-[#FAF6F0]">
      {/* Main Dual-Tone Card Container */}
      <div className="relative flex w-full max-w-5xl flex-col md:flex-row overflow-hidden rounded-[28px] border border-[#4D123B] bg-[#FAF6F0] shadow-2xl">
        
        {/* ================= LEFT HERO PANEL: DEEP BERRY ================= */}
        <div className="relative flex flex-col justify-between overflow-hidden bg-gradient-to-br from-[#24071B] via-[#360B29] to-[#170311] p-8 md:w-5/12 text-[#FAF6F0] border-b md:border-b-0 md:border-r border-[#4D123B]">
          
          {/* Ambient Berry Glow Circles */}
          <div className="pointer-events-none absolute -top-24 -left-24 h-72 w-72 rounded-full bg-[#871658]/35 blur-[80px]" />
          <div className="pointer-events-none absolute -bottom-20 -right-20 h-80 w-80 rounded-full bg-[#A01B69]/25 blur-[90px]" />

          {/* Top Brand & Status */}
          <div className="relative z-10">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#871658] border border-[#FAF6F0]/20 shadow-md">
                  <Sparkles className="h-5 w-5 text-[#FAF6F0]" />
                </div>
                <div>
                  <span className="text-base font-extrabold tracking-tight text-[#FAF6F0]">Agent Studio</span>
                  <p className="text-[10px] font-medium uppercase tracking-wider text-[#FAF6F0]/60">Autonomous IDE</p>
                </div>
              </div>

              <span className="hidden sm:inline-flex items-center gap-1.5 rounded-full bg-[#FAF6F0]/10 px-3 py-1 text-[11px] font-medium text-[#FAF6F0] backdrop-blur-md border border-[#FAF6F0]/15">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Live Engine
              </span>
            </div>
          </div>

          {/* Center Graphic Feature Callouts */}
          <div className="relative z-10 my-10 space-y-4">
            <div className="inline-flex items-center gap-2 rounded-lg bg-[#871658]/40 px-3 py-1 text-xs font-semibold text-[#FAF6F0] border border-[#871658]/60">
              <Layers className="h-3.5 w-3.5 text-[#FAF6F0]" />
              {heroSlides[activeSlide].tag}
            </div>

            <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-[#FAF6F0] leading-snug">
              {heroSlides[activeSlide].title}
            </h2>

            <p className="text-xs sm:text-sm text-[#FAF6F0]/70 leading-relaxed font-normal">
              {heroSlides[activeSlide].description}
            </p>

            {/* Quick architectural badges */}
            <div className="pt-2 flex flex-wrap gap-2 text-[11px] text-[#FAF6F0]/80">
              <span className="inline-flex items-center gap-1 rounded-md bg-[#24071B]/80 px-2 py-1 border border-[#4D123B]">
                <Cpu className="h-3 w-3 text-[#FAF6F0]/70" /> LangGraph Orchestrator
              </span>
              <span className="inline-flex items-center gap-1 rounded-md bg-[#24071B]/80 px-2 py-1 border border-[#4D123B]">
                <ShieldCheck className="h-3 w-3 text-emerald-400" /> Docker Sandbox
              </span>
            </div>
          </div>

          {/* Bottom Interactive Slide Dots */}
          <div className="relative z-10 flex items-center justify-between pt-4 border-t border-[#4D123B]/60">
            <div className="flex gap-2">
              {heroSlides.map((_, idx) => (
                <button
                  key={idx}
                  onClick={() => setActiveSlide(idx)}
                  className={`h-1.5 rounded-full transition-all duration-300 ${
                    activeSlide === idx ? 'w-7 bg-[#FAF6F0]' : 'w-2 bg-[#FAF6F0]/30 hover:bg-[#FAF6F0]/50'
                  }`}
                  aria-label={`Slide ${idx + 1}`}
                />
              ))}
            </div>
            <span className="text-[11px] text-[#FAF6F0]/50 font-mono">v1.0.0 Prod</span>
          </div>
        </div>

        {/* ================= RIGHT AUTH PANEL: VANILLA CLOUD ================= */}
        <div className="flex flex-col justify-center bg-[#FAF6F0] p-8 sm:p-12 md:w-7/12 text-[#24071B]">
          
          <div className="mx-auto w-full max-w-md">
            {/* Header */}
            <div className="mb-6">
              <h3 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-[#24071B]">
                {isLogin ? 'Welcome back' : 'Create an account'}
              </h3>
              <p className="mt-1.5 text-xs sm:text-sm text-[#7A6960]">
                {isLogin ? 'Already building with us? ' : 'Already have an account? '}
                <button
                  type="button"
                  onClick={() => {
                    setIsLogin(!isLogin);
                    setError(null);
                  }}
                  className="font-bold text-[#871658] hover:text-[#A01B69] hover:underline"
                >
                  {isLogin ? 'Register now' : 'Log in'}
                </button>
              </p>
            </div>

            {/* Error Alert */}
            {error && (
              <div className="mb-5 rounded-xl bg-rose-50 border border-rose-200 p-3.5 text-xs text-rose-700 leading-relaxed shadow-sm">
                {error}
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              
              {!isLogin && (
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-[#7A6960] mb-1.5">
                    Username
                  </label>
                  <div className="relative">
                    <UserIcon className="absolute left-3.5 top-3 h-4 w-4 text-[#7A6960]/60" />
                    <input
                      type="text"
                      required
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      placeholder="e.g. dev_coder"
                      className="w-full rounded-xl border border-[#E8DCCF] bg-white py-2.5 pl-10 pr-4 text-sm text-[#24071B] placeholder-[#7A6960]/40 focus:border-[#871658] focus:outline-none focus:ring-2 focus:ring-[#871658]/20 transition-all"
                    />
                  </div>
                </div>
              )}

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-[#7A6960] mb-1.5">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-3 h-4 w-4 text-[#7A6960]/60" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="developer@example.com"
                    className="w-full rounded-xl border border-[#E8DCCF] bg-white py-2.5 pl-10 pr-4 text-sm text-[#24071B] placeholder-[#7A6960]/40 focus:border-[#871658] focus:outline-none focus:ring-2 focus:ring-[#871658]/20 transition-all"
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="block text-xs font-bold uppercase tracking-wider text-[#7A6960]">
                    Password
                  </label>
                  {isLogin && (
                    <button
                      type="button"
                      onClick={() => alert('Password reset service: Check backend SMTP credentials.')}
                      className="text-xs font-semibold text-[#871658] hover:underline"
                    >
                      Forgot?
                    </button>
                  )}
                </div>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-3 h-4 w-4 text-[#7A6960]/60" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full rounded-xl border border-[#E8DCCF] bg-white py-2.5 pl-10 pr-11 text-sm text-[#24071B] placeholder-[#7A6960]/40 focus:border-[#871658] focus:outline-none focus:ring-2 focus:ring-[#871658]/20 transition-all"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-2.5 rounded p-1 text-[#7A6960] hover:text-[#24071B]"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              {/* Terms Checkbox for Sign Up */}
              {!isLogin && (
                <div className="flex items-center gap-2 pt-1">
                  <input
                    id="terms"
                    type="checkbox"
                    checked={agreedToTerms}
                    onChange={(e) => setAgreedToTerms(e.target.checked)}
                    className="h-4 w-4 rounded border-[#E8DCCF] text-[#871658] focus:ring-[#871658]"
                  />
                  <label htmlFor="terms" className="text-xs text-[#7A6960] select-none">
                    I agree to the <span className="font-semibold text-[#871658] hover:underline cursor-pointer">Terms & Conditions</span>
                  </label>
                </div>
              )}

              {/* Submit CTA Button */}
              <button
                type="submit"
                disabled={loading}
                className="group flex w-full items-center justify-center gap-2 rounded-xl bg-[#871658] hover:bg-[#A01B69] py-3 px-4 text-sm font-bold text-[#FAF6F0] shadow-md transition-all active:scale-[0.98] disabled:opacity-50 cursor-pointer"
              >
                {loading ? (
                  <Loader2 className="h-4 w-4 animate-spin text-[#FAF6F0]" />
                ) : (
                  <>
                    <span>{isLogin ? 'Sign In to Workspace' : 'Create Account'}</span>
                    <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                  </>
                )}
              </button>
            </form>

            {/* Divider */}
            <div className="relative my-6 text-center">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-[#E8DCCF]" />
              </div>
              <span className="relative bg-[#FAF6F0] px-3 text-[11px] font-semibold uppercase tracking-wider text-[#7A6960]/70">
                Or continue with
              </span>
            </div>

            {/* Social Auth Providers */}
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => alert('OAuth configuration: Google Client ID required in .env.')}
                className="flex items-center justify-center gap-2 rounded-xl border border-[#E8DCCF] bg-white py-2.5 text-xs font-semibold text-[#24071B] hover:bg-[#F3ECE2] transition-colors shadow-sm"
              >
                <svg className="h-4 w-4" viewBox="0 0 24 24">
                  <path
                    fill="#4285F4"
                    d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.8-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.36 24 12 24z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.98 0 12s.45 3.82 1.25 5.42l4.03-3.15z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.36 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"
                  />
                </svg>
                Google
              </button>

           <button
  type="button"
  onClick={() => alert('OAuth configuration: GitHub App Client ID required in .env.')}
  className="flex items-center justify-center gap-2 rounded-xl border border-[#E8DCCF] bg-white py-2.5 text-xs font-semibold text-[#24071B] hover:bg-[#F3ECE2] transition-colors shadow-sm"
>
  <svg className="h-4 w-4 fill-[#24071B]" viewBox="0 0 24 24" aria-hidden="true">
    <path
      fillRule="evenodd"
      clipRule="evenodd"
      d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
    />
  </svg>
  GitHub
</button>
            </div>

          </div>
        </div>

      </div>
    </div>
  );
};