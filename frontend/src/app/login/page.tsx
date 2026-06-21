"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "../../lib/supabase";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSignUp, setIsSignUp] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // If the user already has a session, redirect to the home screen
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session) {
        router.push("/");
      }
    });
  }, [router]);

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);

    // Simple validation
    if (!email || !password) {
      setError("Please fill in all fields.");
      setLoading(false);
      return;
    }

    try {
      if (isSignUp) {
        const { error } = await supabase.auth.signUp({
          email,
          password,
        });
        if (error) throw error;
        setMessage("Account created! You can now log in (and check email if verification is required).");
        setIsSignUp(false);
      } else {
        const { error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (error) throw error;
        router.push("/");
        router.refresh();
      }
    } catch (err: any) {
      setError(err.message || "An authentication error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-black overflow-hidden font-sans">
      {/* Background Neon Glows */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-indigo-900/20 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-violet-900/20 blur-[120px] pointer-events-none" />

      {/* Main Glassmorphic Card Container */}
      <div className="relative z-10 w-full max-w-md p-8 sm:p-10 mx-4 bg-zinc-950/40 backdrop-blur-xl border border-zinc-800/80 rounded-2xl shadow-2xl transition-all duration-300">
        
        {/* Header */}
        <div className="flex flex-col items-center mb-8">
          <div className="flex items-center justify-center w-12 h-12 mb-3 bg-gradient-to-tr from-indigo-500 to-violet-600 rounded-xl shadow-lg shadow-indigo-500/20">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A13.916 13.916 0 009 11m-6 11h10a5 5 0 005-5v-3.5m0 0A3.5 3.5 0 1113.5 9V5a3.5 3.5 0 00-7 0v3.5a3.5 3.5 0 01-1.5 2.5m6-6V2" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-white">
            Document Copilot
          </h2>
          <p className="mt-2 text-sm text-zinc-400 text-center">
            {isSignUp ? "Create an account to access SEC Filings" : "Sign in to access SEC Filings"}
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleAuth} className="space-y-6">
          
          {/* Email Address */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-zinc-300 mb-2">
              Email Address
            </label>
            <input
              id="email"
              type="email"
              placeholder="analyst@driftwood.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 bg-zinc-900/60 border border-zinc-800 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 placeholder-zinc-600 transition-all duration-200"
              required
            />
          </div>

          {/* Password */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-zinc-300 mb-2">
              Password
            </label>
            <input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 bg-zinc-900/60 border border-zinc-800 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 placeholder-zinc-600 transition-all duration-200"
              required
            />
          </div>

          {/* Alerts */}
          {error && (
            <div className="p-3 bg-red-950/30 border border-red-800/50 text-red-400 text-sm rounded-lg">
              {error}
            </div>
          )}
          {message && (
            <div className="p-3 bg-emerald-950/30 border border-emerald-800/50 text-emerald-400 text-sm rounded-lg">
              {message}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="relative w-full py-3 bg-gradient-to-r from-indigo-500 to-violet-600 hover:from-indigo-600 hover:to-violet-700 text-white font-semibold rounded-lg shadow-lg shadow-indigo-500/10 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Processing...
              </span>
            ) : (
              <span>{isSignUp ? "Create Account" : "Sign In"}</span>
            )}
          </button>
        </form>

        {/* Toggle Mode */}
        <div className="mt-6 text-center">
          <button
            type="button"
            onClick={() => {
              setIsSignUp(!isSignUp);
              setError(null);
              setMessage(null);
            }}
            className="text-sm text-indigo-400 hover:text-indigo-300 font-medium transition-colors duration-150 focus:outline-none"
          >
            {isSignUp ? "Already have an account? Sign In" : "Don't have an account? Sign Up"}
          </button>
        </div>

      </div>
    </div>
  );
}
