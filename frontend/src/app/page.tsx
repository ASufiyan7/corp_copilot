"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../hooks/useAuth";
import { env } from "../lib/env";

interface BackendProfile {
  id: string;
  email: string;
  created_at: string;
}

export default function Home() {
  const router = useRouter();
  const { user, session, loading, signOut } = useAuth();
  const [backendProfile, setBackendProfile] = useState<BackendProfile | null>(null);
  const [backendError, setBackendError] = useState<string | null>(null);
  const [verifying, setVerifying] = useState(false);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    }
  }, [user, loading, router]);

  // Call backend verification once session is available
  useEffect(() => {
    if (session?.access_token) {
      setVerifying(true);
      setBackendError(null);
      
      const apiBase = env.API_BASE_URL;
      
      fetch(`${apiBase}/api/auth/me`, {
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      })
        .then((res) => {
          if (!res.ok) {
            throw new Error(`Server returned status ${res.status}`);
          }
          return res.json();
        })
        .then((data: BackendProfile) => {
          setBackendProfile(data);
        })
        .catch((err: Error) => {
          console.error("Backend auth verification failed:", err);
          setBackendError(err.message || "Failed to verify session with backend.");
        })
        .finally(() => {
          setVerifying(false);
        });
    }
  }, [session]);

  const handleLogout = async () => {
    await signOut();
    router.push("/login");
  };

  if (loading || (!user && !loading)) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-black text-white font-sans">
        <div className="relative flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin" />
          <p className="text-zinc-400 text-sm tracking-wide animate-pulse">
            Verifying secure session...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen bg-black text-white font-sans overflow-hidden">
      {/* Ambient backgrounds */}
      <div className="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-violet-900/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-indigo-900/10 blur-[120px] pointer-events-none" />

      {/* Navigation Header */}
      <header className="relative z-10 border-b border-zinc-900 bg-zinc-950/20 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 flex items-center justify-center bg-gradient-to-tr from-indigo-500 to-violet-600 rounded-lg shadow-lg">
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A13.916 13.916 0 009 11m-6 11h10a5 5 0 005-5v-3.5m0 0A3.5 3.5 0 1113.5 9V5a3.5 3.5 0 00-7 0v3.5a3.5 3.5 0 01-1.5 2.5m6-6V2" />
              </svg>
            </div>
            <span className="font-bold tracking-tight text-white">Document Copilot</span>
          </div>

          <div className="flex items-center gap-4">
            <span className="text-xs text-zinc-400 hidden sm:inline">
              Authenticated: <span className="text-zinc-200 font-mono">{user?.email}</span>
            </span>
            <button
              onClick={handleLogout}
              className="px-4 py-2 border border-zinc-800 hover:bg-zinc-900 text-zinc-300 hover:text-white text-xs font-semibold rounded-lg transition-colors duration-150"
            >
              Sign Out
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="relative z-10 max-w-4xl mx-auto px-6 py-12">
        
        {/* Welcome Section */}
        <div className="mb-10 text-center sm:text-left">
          <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl bg-clip-text text-transparent bg-gradient-to-r from-white via-zinc-200 to-zinc-500">
            Welcome back to research
          </h1>
          <p className="mt-2 text-zinc-400 text-sm sm:text-base max-w-xl">
            You are securely logged in. The database models, full-text indexes, and backend authentication protocols have been initialized.
          </p>
        </div>

        {/* Verification Cards */}
        <div className="grid gap-6 md:grid-cols-2">
          
          {/* Frontend Session Card */}
          <div className="p-6 bg-zinc-950/40 border border-zinc-800/80 rounded-xl backdrop-blur-md">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-zinc-400 mb-4">
              Frontend Client Session
            </h3>
            <div className="space-y-3 text-sm">
              <div>
                <span className="text-zinc-500 block text-xs">Provider</span>
                <span className="text-zinc-200 font-medium">Supabase Authentication</span>
              </div>
              <div>
                <span className="text-zinc-500 block text-xs">User ID (JWT subject)</span>
                <span className="text-zinc-200 font-mono text-xs break-all">{user?.id}</span>
              </div>
              <div>
                <span className="text-zinc-500 block text-xs">Email Address</span>
                <span className="text-zinc-200 font-mono text-xs">{user?.email}</span>
              </div>
            </div>
          </div>

          {/* Backend Verification Card */}
          <div className="p-6 bg-zinc-950/40 border border-zinc-800/80 rounded-xl backdrop-blur-md">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-zinc-400 mb-4">
              Backend Integration Status
            </h3>

            {verifying && (
              <div className="flex items-center gap-3 text-zinc-400 text-sm py-4">
                <div className="w-4 h-4 border-2 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin" />
                <span>Verifying credentials with FastAPI...</span>
              </div>
            )}

            {!verifying && backendProfile && (
              <div className="space-y-3 text-sm">
                <div className="flex items-center gap-2 text-emerald-400 font-semibold mb-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Backend Authenticated: OK</span>
                </div>
                <div>
                  <span className="text-zinc-500 block text-xs">Local DB Profile ID</span>
                  <span className="text-zinc-200 font-mono text-xs break-all">{backendProfile.id}</span>
                </div>
                <div>
                  <span className="text-zinc-500 block text-xs">Profile Registered At</span>
                  <span className="text-zinc-200 text-xs">
                    {new Date(backendProfile.created_at).toLocaleString()}
                  </span>
                </div>
              </div>
            )}

            {!verifying && backendError && (
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-red-400 font-semibold">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Verification Failed</span>
                </div>
                <p className="text-xs text-red-300/80 bg-red-950/20 p-3 rounded-lg border border-red-900/30">
                  {backendError}
                </p>
              </div>
            )}
          </div>

        </div>

      </main>
    </div>
  );
}
