import { useState, useEffect } from "react";
import { apiFetch } from "../lib/api";
import { useAuth } from "./useAuth";

export interface Thread {
  id: string;
  title: string;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export function useThreads() {
  const { user } = useAuth();
  const [threads, setThreads] = useState<Thread[]>([]);
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchThreads = async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const data = await apiFetch<Thread[]>("/api/threads");
      setThreads(data);
    } catch (err: any) {
      console.warn("Backend /api/threads not available, using client-side mock threads.", err);
      // Fallback: Read mock data from localStorage
      const stored = localStorage.getItem(`threads_${user.id}`);
      if (stored) {
        setThreads(JSON.parse(stored));
      } else {
        // Initial mock threads for rich UX in Phase 3
        const mockThreads: Thread[] = [
          {
            id: "thread-1",
            title: "Apple 2021-2025 Revenue Mix Shift",
            user_id: user.id,
            created_at: new Date(Date.now() - 3600000 * 2).toISOString(),
            updated_at: new Date(Date.now() - 3600000 * 2).toISOString(),
          },
          {
            id: "thread-2",
            title: "NVIDIA Data Center AI Demand Analysis",
            user_id: user.id,
            created_at: new Date(Date.now() - 3600000 * 24).toISOString(),
            updated_at: new Date(Date.now() - 3600000 * 24).toISOString(),
          }
        ];
        localStorage.setItem(`threads_${user.id}`, JSON.stringify(mockThreads));
        setThreads(mockThreads);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchThreads();
    }
  }, [user]);

  const createThread = async (title: string = "New Research Chat") => {
    if (!user) return null;
    const newThreadId = crypto.randomUUID();
    const newThread: Thread = {
      id: newThreadId,
      title,
      user_id: user.id,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    try {
      const response = await apiFetch<Thread>("/api/threads", {
        method: "POST",
        body: JSON.stringify({ title, id: newThreadId }),
      });
      setThreads((prev) => [response, ...prev]);
      setActiveThreadId(response.id);
      return response.id;
    } catch (err) {
      const updatedThreads = [newThread, ...threads];
      setThreads(updatedThreads);
      localStorage.setItem(`threads_${user.id}`, JSON.stringify(updatedThreads));
      setActiveThreadId(newThread.id);
      return newThread.id;
    }
  };

  const deleteThread = async (threadId: string) => {
    if (!user) return;
    try {
      await apiFetch(`/api/threads/${threadId}`, { method: "DELETE" });
      setThreads((prev) => prev.filter((t) => t.id !== threadId));
    } catch (err) {
      const updatedThreads = threads.filter((t) => t.id !== threadId);
      setThreads(updatedThreads);
      localStorage.setItem(`threads_${user.id}`, JSON.stringify(updatedThreads));
    }
    if (activeThreadId === threadId) {
      setActiveThreadId(null);
    }
  };

  const updateThreadTitle = async (threadId: string, title: string) => {
    if (!user) return;
    try {
      const response = await apiFetch<Thread>(`/api/threads/${threadId}`, {
        method: "PATCH",
        body: JSON.stringify({ title }),
      });
      setThreads((prev) => prev.map((t) => (t.id === threadId ? response : t)));
    } catch (err) {
      const updatedThreads = threads.map((t) =>
        t.id === threadId ? { ...t, title, updated_at: new Date().toISOString() } : t
      );
      setThreads(updatedThreads);
      localStorage.setItem(`threads_${user.id}`, JSON.stringify(updatedThreads));
    }
  };

  return {
    threads,
    activeThreadId,
    setActiveThreadId,
    loading,
    error,
    createThread,
    deleteThread,
    updateThreadTitle,
    refreshThreads: fetchThreads,
  };
}
