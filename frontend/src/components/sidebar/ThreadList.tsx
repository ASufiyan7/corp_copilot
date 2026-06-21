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
    <aside className="w-80 flex flex-col bg-zinc-950 border-r border-zinc-900 text-zinc-300">
      
      {/* Sidebar Header */}
      <div className="p-4 border-b border-zinc-900">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-8 h-8 flex items-center justify-center bg-gradient-to-tr from-indigo-500 to-violet-600 rounded-lg shadow-lg shadow-indigo-500/20">
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A13.916 13.916 0 009 11m-6 11h10a5 5 0 005-5v-3.5m0 0A3.5 3.5 0 1113.5 9V5a3.5 3.5 0 00-7 0v3.5a3.5 3.5 0 01-1.5 2.5m6-6V2" />
            </svg>
          </div>
          <span className="font-bold tracking-tight text-white text-base">Document Copilot</span>
        </div>

        <button
          onClick={handleCreate}
          disabled={creating}
          className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-zinc-900 hover:bg-zinc-850 text-white hover:text-white border border-zinc-800 hover:border-zinc-700 font-medium rounded-lg text-sm shadow-sm transition-all duration-200 disabled:opacity-50"
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
        <h3 className="px-3 py-2 text-xs font-semibold uppercase tracking-wider text-zinc-500">
          Saved Conversations
        </h3>
        
        {loading && threads.length === 0 ? (
          <div className="flex items-center justify-center p-8 gap-2 text-zinc-500 text-xs">
            <Loader2 className="w-4 h-4 animate-spin" />
            Loading conversations...
          </div>
        ) : threads.length === 0 ? (
          <div className="px-3 py-6 text-zinc-500 text-xs text-center">
            No research conversations found.
          </div>
        ) : (
          threads.map((thread) => {
            const isActive = thread.id === activeThreadId;
            return (
              <div
                key={thread.id}
                onClick={() => setActiveThreadId(thread.id)}
                className={`group flex items-center justify-between px-3 py-2.5 rounded-lg text-sm cursor-pointer transition-all duration-150 ${
                  isActive
                    ? "bg-zinc-900 text-white font-medium border border-zinc-800"
                    : "hover:bg-zinc-900/50 hover:text-zinc-200 border border-transparent"
                }`}
              >
                <div className="flex items-center gap-2.5 overflow-hidden flex-1">
                  <MessageSquare className={`w-4 h-4 flex-shrink-0 ${isActive ? "text-indigo-400" : "text-zinc-500"}`} />
                  <span className="truncate pr-2">{thread.title || "Untitled Chat"}</span>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteThread(thread.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 hover:text-red-400 p-1 rounded hover:bg-zinc-800 text-zinc-500 transition-all duration-150"
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
      <div className="p-4 border-t border-zinc-900 bg-zinc-950/80">
        <div className="flex flex-col gap-2">
          {userEmail && (
            <div className="text-xs text-zinc-500 truncate px-1">
              User: <span className="text-zinc-300 font-mono">{userEmail}</span>
            </div>
          )}
          <button
            onClick={onLogout}
            className="w-full flex items-center justify-center gap-2 py-2 px-3 hover:bg-zinc-900 text-zinc-400 hover:text-red-400 border border-transparent hover:border-zinc-850 text-xs font-semibold rounded-lg transition-all duration-150"
          >
            Sign Out
          </button>
        </div>
      </div>

    </aside>
  );
}
