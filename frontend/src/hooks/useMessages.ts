import { useState, useEffect } from "react";
import { apiFetch, apiFetchStream } from "../lib/api";

export interface Citation {
  chunk_id: string;
  document_id: string;
  excerpt: string;
  ticker?: string;
  company_name?: string;
  filing_type?: string;
  filing_date?: string;
}

export interface Message {
  id: string;
  thread_id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
  citations?: Citation[];
}

export function useMessages(threadId: string | null) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMessages = async () => {
    if (!threadId) {
      setMessages([]);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await apiFetch<Message[]>(`/api/threads/${threadId}`);
      setMessages(data);
    } catch (err: any) {
      console.warn("Backend thread messages not available, using mock messages.", err);
      // Fallback: Read mock messages from localStorage
      const stored = localStorage.getItem(`messages_${threadId}`);
      if (stored) {
        setMessages(JSON.parse(stored));
      } else {
        // Initial mock messages depending on threadId for a rich UX
        let mockMsgs: Message[] = [];
        if (threadId === "thread-1") {
          mockMsgs = [
            {
              id: "msg-1-1",
              thread_id: threadId,
              role: "user",
              content: "How did Apple's revenue mix shift between 2021 and 2025?",
              created_at: new Date(Date.now() - 3600000 * 2).toISOString(),
            },
            {
              id: "msg-1-2",
              thread_id: threadId,
              role: "assistant",
              content: "Between fiscal years 2021 and 2025, Apple's revenue mix showed a steady shift towards Services. While iPhone remained the largest single revenue contributor (accounting for ~50-52% of total sales), Services revenue grew from $68.4 billion in FY21 to over $95 billion in FY25, now representing approximately 25% of total sales. Other segments like iPad and Wearables fluctuated slightly due to supply constraints and product release cycles.",
              created_at: new Date(Date.now() - 3600000 * 2 + 10000).toISOString(),
              citations: [
                {
                  chunk_id: "chunk-aapl-1",
                  document_id: "doc-aapl",
                  excerpt: "Services net sales were $85,200 million in 2024 and $68,425 million in 2022. Services revenue represents approximately 22% of total net sales.",
                  ticker: "AAPL",
                  filing_type: "10-K",
                  filing_date: "2024-10-31"
                }
              ]
            }
          ];
        } else if (threadId === "thread-2") {
          mockMsgs = [
            {
              id: "msg-2-1",
              thread_id: threadId,
              role: "user",
              content: "What did NVIDIA say about AI demand in 2025?",
              created_at: new Date(Date.now() - 3600000 * 24).toISOString(),
            },
            {
              id: "msg-2-2",
              thread_id: threadId,
              role: "assistant",
              content: "In its fiscal 2025 filings, NVIDIA described demand for its Hopper and Blackwell GPU architectures as 'exceptional' and 'unprecedented'. The company highlighted that demand was significantly outstripping supply, particularly for Blackwell platform components, and expected supply constraints to continue through several quarters of fiscal 2026. Data Center segment revenue surged over 100% year-over-year, driven by cloud service providers, consumer internet companies, and enterprise AI deployments.",
              created_at: new Date(Date.now() - 3600000 * 24 + 15000).toISOString(),
              citations: [
                {
                  chunk_id: "chunk-nvda-1",
                  document_id: "doc-nvda",
                  excerpt: "Demand for Blackwell remains exceptional, and we are working hard to ramp up production to satisfy customer needs. Our Data Center segment revenue grew to $22.6 billion, up 427% year-over-year.",
                  ticker: "NVDA",
                  filing_type: "10-K",
                  filing_date: "2025-02-26"
                }
              ]
            }
          ];
        }
        localStorage.setItem(`messages_${threadId}`, JSON.stringify(mockMsgs));
        setMessages(mockMsgs);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMessages();
  }, [threadId]);

  const sendMessage = async (content: string) => {
    if (!threadId) return;
    const userMsgId = crypto.randomUUID();
    const userMsg: Message = {
      id: userMsgId,
      thread_id: threadId,
      role: "user",
      content,
      created_at: new Date().toISOString(),
    };

    // Update local state optimistically
    const updatedWithUser = [...messages, userMsg];
    setMessages(updatedWithUser);
    localStorage.setItem(`messages_${threadId}`, JSON.stringify(updatedWithUser));

    setLoading(true);
    setError(null);

    try {
      const response = await apiFetchStream("/api/chat/stream", {
        method: "POST",
        body: JSON.stringify({ threadId, message: content }),
      });

      if (!response.body) {
        throw new Error("No response body available for stream");
      }

      const assistantMsgId = crypto.randomUUID();
      let assistantMsg: Message = {
        id: assistantMsgId,
        thread_id: threadId,
        role: "assistant",
        content: "",
        created_at: new Date().toISOString(),
        citations: [],
      };

      setMessages([...updatedWithUser, assistantMsg]);

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        let boundary = buffer.indexOf("\n\n");
        while (boundary !== -1) {
          const messageBlock = buffer.slice(0, boundary).trim();
          buffer = buffer.slice(boundary + 2);

          let eventType = "message";
          let dataStr = "";

          const lines = messageBlock.split("\n");
          for (const line of lines) {
            if (line.startsWith("event:")) {
              eventType = line.slice(6).trim();
            } else if (line.startsWith("data:")) {
              dataStr = line.slice(5).trim();
            }
          }

          if (dataStr) {
            try {
              const data = JSON.parse(dataStr);
              if (eventType === "text-delta") {
                assistantMsg.content += data.delta;
                setMessages((prev) =>
                  prev.map((m) => (m.id === assistantMsgId ? { ...assistantMsg } : m))
                );
              } else if (eventType === "citation") {
                if (!assistantMsg.citations) assistantMsg.citations = [];
                if (!assistantMsg.citations.some((c) => c.chunk_id === data.chunk_id)) {
                  assistantMsg.citations = [...assistantMsg.citations, data];
                  setMessages((prev) =>
                    prev.map((m) => (m.id === assistantMsgId ? { ...assistantMsg } : m))
                  );
                }
              } else if (eventType === "complete") {
                assistantMsg = {
                  id: data.id,
                  thread_id: threadId,
                  role: "assistant",
                  content: data.content,
                  created_at: data.created_at,
                  citations: data.citations,
                };
                setMessages((prev) =>
                  prev.map((m) => (m.id === assistantMsgId ? { ...assistantMsg } : m))
                );
                
                const finalMessages = [...updatedWithUser, assistantMsg];
                localStorage.setItem(`messages_${threadId}`, JSON.stringify(finalMessages));
              } else if (eventType === "error") {
                throw new Error(data.detail || "Error streaming response");
              }
            } catch (err) {
              console.warn("Error parsing event data:", err);
            }
          }

          boundary = buffer.indexOf("\n\n");
        }
      }
      setLoading(false);
    } catch (err: any) {
      console.warn("Backend stream failed or not supported. Falling back to mock simulation.", err);
      // Mock assistant response simulation for UI validation when backend is not up
      setTimeout(() => {
        const assistantMsg: Message = {
          id: crypto.randomUUID(),
          thread_id: threadId,
          role: "assistant",
          content: `Thank you for your question: "${content}". This is a mock response from the Research Assistant. In Phase 4, the real LLM engine and vector store will parse SEC filings to provide grounded answers here.`,
          created_at: new Date().toISOString(),
          citations: [
            {
              chunk_id: "mock-chunk",
              document_id: "mock-doc",
              excerpt: "This is a placeholder passage representing SEC filing evidence that will back this claim in later phases.",
              ticker: "MOCK",
              filing_type: "10-K",
              filing_date: "2025-01-01"
            }
          ]
        };
        const finalMessages = [...updatedWithUser, assistantMsg];
        setMessages(finalMessages);
        localStorage.setItem(`messages_${threadId}`, JSON.stringify(finalMessages));
        setLoading(false);
      }, 1000);
    }
  };

  return {
    messages,
    loading,
    error,
    sendMessage,
    refreshMessages: fetchMessages,
  };
}
