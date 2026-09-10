import React, { useState } from "react";
import { ShieldAlert, Lock, User, ArrowRight, ShieldCheck } from "lucide-react";
import { UserSession } from "../types";
import { loginUser } from "../api";

interface LoginPageProps {
  onLoginSuccess: (session: UserSession) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState("auditor");
  const [password, setPassword] = useState("auditor123");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const session = await loginUser(username, password);
      onLoginSuccess(session);
    } catch (err: any) {
      setError("Invalid credentials. Please select one of the 1-click test roles below.");
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = async (user: string, pass: string) => {
    setUsername(user);
    setPassword(pass);
    setError(null);
    setLoading(true);
    try {
      const session = await loginUser(user, pass);
      onLoginSuccess(session);
    } catch (err) {
      setError("Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center items-center p-4 relative overflow-hidden">
      {/* Background Subtle Gradient Blobs */}
      <div className="absolute -top-40 -left-40 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />

      {/* Main Login Card */}
      <div className="w-full max-w-md bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden relative z-10 animate-in fade-in zoom-in-95 duration-200">
        {/* Top Header Banner */}
        <div className="bg-slate-900 p-6 text-white text-center border-b border-slate-800">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-blue-600 shadow-lg shadow-blue-500/30 mb-3 border border-blue-400/30">
            <ShieldAlert className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-xl font-black tracking-tight text-white">NIRIKSHAN AI</h1>
          <p className="text-xs text-slate-400 mt-1">
            Ministry of Statistics & Programme Implementation (MoSPI)
          </p>
          <div className="mt-2 inline-flex items-center gap-1 text-[10px] text-blue-300 font-mono bg-blue-950/80 px-2 py-0.5 rounded border border-blue-800">
            <span>SIH26102 • MPLADS DECISION SUPPORT</span>
          </div>
        </div>

        {/* Login Form */}
        <div className="p-6 space-y-5">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl font-medium">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4 text-xs">
            <div>
              <label className="block font-bold text-slate-700 uppercase tracking-wider text-[10px] mb-1.5">
                Username / Officer ID
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-900"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block font-bold text-slate-700 uppercase tracking-wider text-[10px] mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-900"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl transition shadow-md shadow-blue-600/20 flex items-center justify-center gap-2"
            >
              <span>{loading ? "Authenticating..." : "Sign In to Portal"}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* 1-Click Demo Login for Evaluators & Judges */}
          <div className="pt-4 border-t border-slate-100 space-y-2">
            <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider text-center">
              Quick 1-Click Demo Role Presets
            </span>

            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => handleQuickLogin("auditor", "auditor123")}
                className="p-2.5 rounded-xl border border-blue-200 bg-blue-50/50 hover:bg-blue-100/70 text-blue-900 text-center transition"
              >
                <div className="font-bold text-xs">Auditor</div>
                <div className="text-[9px] text-blue-600">CAG Audit</div>
              </button>

              <button
                type="button"
                onClick={() => handleQuickLogin("officer", "officer123")}
                className="p-2.5 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-800 text-center transition"
              >
                <div className="font-bold text-xs">Officer</div>
                <div className="text-[9px] text-slate-500">MoSPI Div</div>
              </button>

              <button
                type="button"
                onClick={() => handleQuickLogin("admin", "admin123")}
                className="p-2.5 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-800 text-center transition"
              >
                <div className="font-bold text-xs">Admin</div>
                <div className="text-[9px] text-slate-500">Data Centre</div>
              </button>
            </div>
          </div>
        </div>

        {/* Card Footer */}
        <div className="px-6 py-3 bg-slate-50 border-t border-slate-100 text-center text-[11px] text-slate-500 flex items-center justify-center gap-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
          <span>Demo Authentication • No Restricted eSAKSHI Scraping Attempted</span>
        </div>
      </div>
    </div>
  );
};
