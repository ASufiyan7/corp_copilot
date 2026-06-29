"use client";

import React from "react";
import { Plus, MessageSquare, Trash2, Loader2 } from "lucide-react";
import { Thread } from "../../hooks/useThreads";

interface ThreadListProps {
  threads: Thread[];
  activeThreadId: string | null;
  setActiveThreadId: (id: string | null) => void;
  createThread: (title?: string) => Promise<string | null>;
  deleteThread: (id: string) => Promise<void>;
  loading: boolean;
  userEmail?: string;
  onLogout: () => void;
}

export default function ThreadList({
  threads,
  activeThreadId,
  setActiveThreadId,
  createThread,
  deleteThread,
  loading,
  userEmail,
  onLogout
}: ThreadListProps) {
  const [creating, setCreating] = React.useState(false);

  const handleCreate = async () => {
    setCreating(true);
    try {
      await createThread();
    } finally {
      setCreating(false);
    }
  };

  return (
    <aside className="w-80 flex flex-col bg-zinc-950/80 backdrop-blur-md border-r border-zinc-900 text-zinc-300 select-none">
      
      {/* Sidebar Header */}
      <div className="p-4 border-b border-zinc-900">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-9 h-9 flex items-center justify-center bg-gradient-to-tr from-indigo-500 to-violet-600 rounded-xl shadow-lg shadow-indigo-500/20 transition-transform duration-300 hover:rotate-3">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A13.916 13.916 0 009 11m-6 11h10a5 5 0 005-5v-3.5m0 0A3.5 3.5 0 1113.5 9V5a3.5 3.5 0 00-7 0v3.5a3.5 3.5 0 01-1.5 2.5m6-6V2" />
            </svg>
          </div>
          <span className="font-bold tracking-tight text-white text-base">Document Copilot</span>
        </div>

        <button
          onClick={handleCreate}
          disabled={creating}
          className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-zinc-900/50 hover:bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-white font-medium rounded-xl text-sm shadow-sm transition-all duration-200 active:scale-[0.98] disabled:opacity-50 cursor-pointer"
        >
          {creating ? (
            <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
          ) : (
            <Plus className="w-4 h-4 text-indigo-400" />
          )}
          New Research Chat
        </button>
      </div>

      {/* Sidebar Thread List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-1 scrollbar-thin">
        <h3 className="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-zinc-500">
          Saved Conversations
        </h3>
        
        {loading && threads.length === 0 ? (
          <div className="flex items-center justify-center p-8 gap-2 text-zinc-500 text-xs">
            <Loader2 className="w-4 h-4 animate-spin text-indigo-500" />
            Loading conversations...
          </div>
        ) : threads.length === 0 ? (
          <div className="px-3 py-8 text-zinc-500 text-xs text-center border border-dashed border-zinc-900 rounded-xl m-1">
            No research conversations found.
          </div>
        ) : (
          threads.map((thread) => {
            const isActive = thread.id === activeThreadId;
            return (
              <div
                key={thread.id}
                onClick={() => setActiveThreadId(thread.id)}
                className={`group flex items-center justify-between px-3 py-2.5 rounded-xl text-sm cursor-pointer transition-all duration-200 ${
                  isActive
                    ? "bg-zinc-900 text-white font-medium border border-zinc-800/80 shadow-md shadow-black/10"
                    : "text-zinc-400 hover:bg-zinc-900/40 hover:text-zinc-200 border border-transparent"
                }`}
              >
                <div className="flex items-center gap-2.5 overflow-hidden flex-1">
                  <MessageSquare className={`w-4 h-4 flex-shrink-0 transition-colors duration-200 ${isActive ? "text-indigo-400" : "text-zinc-650 group-hover:text-zinc-400"}`} />
                  <span className="truncate pr-2">{thread.title || "Untitled Chat"}</span>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteThread(thread.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 focus:opacity-100 hover:text-red-400 p-1.5 rounded-lg hover:bg-red-950/20 text-zinc-500 transition-all duration-200 transform scale-95 hover:scale-100 active:scale-90"
                  title="Delete conversation"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            );
          })
        )}
      </div>

      {/* Sidebar Footer */}
      <div className="p-4 border-t border-zinc-900 bg-zinc-950/40 backdrop-blur-sm">
        <div className="flex flex-col gap-3">
          {userEmail && (
            <div className="flex items-center gap-2.5 px-1">
              <div className="w-8 h-8 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-[10px] font-bold text-indigo-400 uppercase shadow-inner">
                {userEmail.substring(0, 2)}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-[9px] text-zinc-500 font-bold uppercase tracking-wider leading-none mb-1">Research Analyst</p>
                <p className="text-xs text-zinc-300 font-mono truncate leading-none">{userEmail}</p>
              </div>
            </div>
          )}
          <button
            onClick={onLogout}
            className="w-full flex items-center justify-center gap-2 py-2 px-3 hover:bg-red-950/15 text-zinc-400 hover:text-red-400 border border-transparent hover:border-red-900/20 text-xs font-semibold rounded-lg transition-all duration-200 cursor-pointer"
          >
            Sign Out
          </button>
        </div>
      </div>

    </aside>
  );
}
