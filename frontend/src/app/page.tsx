"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Compass, Plus, Loader2 } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { useThreads } from "../hooks/useThreads";
import { useMessages } from "../hooks/useMessages";
import ThreadList from "../components/sidebar/ThreadList";
import ChatWindow from "../components/chat/ChatWindow";

export default function Home() {
  const router = useRouter();
  const { user, loading: authLoading, signOut } = useAuth();
  
  const {
    threads,
    activeThreadId,
    setActiveThreadId,
    loading: threadsLoading,
    createThread,
    deleteThread,
  } = useThreads();

  const {
    messages,
    loading: messagesLoading,
    sendMessage,
  } = useMessages(activeThreadId);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [user, authLoading, router]);

  const handleLogout = async () => {
    await signOut();
    router.push("/login");
  };

  if (authLoading || (!user && !authLoading)) {
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

  // Find the currently active thread object to get its title
  const activeThread = threads.find((t) => t.id === activeThreadId);

  return (
    <div className="flex h-screen bg-black text-white font-sans overflow-hidden">
      
      {/* Left Sidebar Thread Manager */}
      <ThreadList
        threads={threads}
        activeThreadId={activeThreadId}
        setActiveThreadId={setActiveThreadId}
        createThread={createThread}
        deleteThread={deleteThread}
        loading={threadsLoading}
        userEmail={user?.email || ""}
        onLogout={handleLogout}
      />

      {/* Right Chat Panel Workspace */}
      <div className="flex-1 flex flex-col min-w-0 bg-zinc-950/20 overflow-hidden">
        {activeThreadId && activeThread ? (
          <ChatWindow
            threadTitle={activeThread.title}
            messages={messages}
            loading={messagesLoading}
            onSendMessage={sendMessage}
          />
        ) : (
          /* Landing/Welcome screen if no active thread is selected */
          <div className="flex-1 flex flex-col items-center justify-center p-8 text-center relative overflow-hidden bg-zinc-950/20 dot-grid">
            {/* Ambient Background Neon Glows */}
            <div className="absolute top-[15%] right-[10%] w-[45%] h-[45%] rounded-full bg-violet-600/5 blur-[130px] pointer-events-none animate-float-medium" />
            <div className="absolute bottom-[15%] left-[10%] w-[45%] h-[45%] rounded-full bg-indigo-500/5 blur-[130px] pointer-events-none animate-float-slow" />
            
            <div className="relative z-10 max-w-md flex flex-col items-center animate-fade-in-up">
              <div className="w-16 h-16 flex items-center justify-center bg-zinc-900 border border-zinc-800 text-indigo-400 rounded-2xl mb-6 shadow-xl hover:scale-105 hover:border-zinc-750 hover:text-indigo-300 transition-all duration-300 hover:shadow-indigo-500/5">
                <Compass className="w-8 h-8 animate-pulse text-indigo-450" />
              </div>
              <h2 className="text-2.5xl font-extrabold tracking-tight text-white mb-3.5 bg-clip-text text-transparent bg-gradient-to-r from-white via-zinc-200 to-zinc-400">
                SEC Research Workspace
              </h2>
              <p className="text-zinc-450 text-sm leading-relaxed mb-9">
                Select an existing research conversation from the saved history sidebar, or click below to start a new chat querying Apple, Microsoft, NVIDIA, Amazon, or Alphabet filings.
              </p>
              
              <button
                onClick={() => createThread()}
                className="flex items-center justify-center gap-2 py-3.5 px-6 bg-gradient-to-tr from-indigo-500 to-violet-600 hover:from-indigo-650 hover:to-violet-700 text-white font-bold rounded-xl shadow-lg hover:shadow-indigo-500/20 active:scale-[0.98] focus:outline-none focus:ring-2 focus:ring-indigo-500/30 transition-all duration-200 cursor-pointer"
              >
                <Plus className="w-5 h-5 text-indigo-200" />
                Start New Research
              </button>
            </div>
          </div>
        )}
      </div>

    </div>
  );
}
