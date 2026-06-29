"use client";

import React, { useRef, useEffect } from "react";
import { Cpu, Terminal, Compass } from "lucide-react";
import { Message } from "../../hooks/useMessages";
import MessageBubble from "./MessageBubble";
import ChatInput from "./ChatInput";

interface ChatWindowProps {
  threadTitle: string;
  messages: Message[];
  loading: boolean;
  onSendMessage: (content: string) => void;
}

const SAMPLE_PROMPTS = [
  {
    title: "Apple Revenue Shift",
    text: "Across Apple's 2021–2025 10-Ks, how did the revenue mix between iPhone, Services, Mac, iPad, and Wearables change?",
  },
  {
    title: "NVIDIA Data Center AI",
    text: "How did NVIDIA describe demand drivers, customer concentration, and supply constraints for its Data Center business from fiscal 2021 through fiscal 2025?",
  },
  {
    title: "Amazon AWS Margin",
    text: "For Amazon, compare AWS operating income and margin against North America and International from 2021–2025.",
  },
  {
    title: "Microsoft Azure Capacity",
    text: "Across Microsoft's 2021–2025 filings, what changed in the way the company describes Azure, AI infrastructure, and cloud capacity constraints?",
  }
];

export default function ChatWindow({
  threadTitle,
  messages,
  loading,
  onSendMessage
}: ChatWindowProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto scroll to the bottom of the list when messages change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="flex-1 flex flex-col bg-zinc-950/30 text-white overflow-hidden dot-grid relative">
      
      {/* Thread Chat Header */}
      <div className="h-16 flex-shrink-0 flex items-center justify-between px-6 border-b border-zinc-900 bg-zinc-950/60 backdrop-blur-md z-10">
        <div className="flex items-center gap-2.5">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
          <h2 className="text-sm font-bold text-white truncate max-w-lg tracking-tight">
            {threadTitle || "Research Conversation"}
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[9px] bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 font-bold uppercase tracking-wider px-2.5 py-1 rounded-lg">
            Grounded RAG Mode
          </span>
        </div>
      </div>

      {/* Message History Scrolling Container */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin"
      >
        {messages.length === 0 ? (
          /* Empty/Welcome State showing Sample Prompts */
          <div className="max-w-2xl mx-auto py-16 flex flex-col items-center animate-fade-in-up">
            
            <div className="w-14 h-14 flex items-center justify-center bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-2xl mb-5 shadow-inner">
              <Compass className="w-7 h-7 animate-pulse text-indigo-400" />
            </div>
            
            <h2 className="text-2xl font-extrabold tracking-tight text-white mb-2 bg-clip-text text-transparent bg-gradient-to-r from-white via-zinc-200 to-zinc-400">
              SEC Filing Intelligence Copilot
            </h2>
            <p className="text-sm text-zinc-450 text-center max-w-md mb-10 leading-relaxed">
              Ask a question about S&P 500 company filings. Document Copilot will fetch the filings, extract citations, and construct grounded answers.
            </p>

            <div className="grid gap-4 sm:grid-cols-2 w-full">
              {SAMPLE_PROMPTS.map((prompt, idx) => (
                <div
                  key={idx}
                  onClick={() => onSendMessage(prompt.text)}
                  className="group p-4.5 glass-card hover:bg-zinc-900/40 border border-zinc-900/60 hover:border-indigo-500/30 rounded-2xl cursor-pointer text-left transition-all duration-300 hover:scale-[1.02] hover:shadow-lg hover:shadow-indigo-950/5 active:scale-[0.99]"
                >
                  <h4 className="text-[10px] font-bold uppercase tracking-wider text-indigo-400 mb-1.5 group-hover:text-indigo-350 transition-colors duration-255">
                    {prompt.title}
                  </h4>
                  <p className="text-zinc-300 text-xs leading-relaxed line-clamp-3">
                    {prompt.text}
                  </p>
                </div>
              ))}
            </div>

          </div>
        ) : (
          /* Render Active Message History */
          <div className="max-w-3xl mx-auto space-y-6">
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            
            {/* Loading/Responding Indicator bubble */}
            {loading && messages[messages.length - 1]?.role === "user" && (
              <div className="flex gap-4 w-full justify-start items-center animate-fade-in-up">
                <div className="w-8.5 h-8.5 flex-shrink-0 flex items-center justify-center bg-gradient-to-tr from-indigo-500 to-violet-600 text-white rounded-xl shadow-lg shadow-indigo-500/10">
                  <Cpu className="w-4 h-4" />
                </div>
                <div className="flex items-center gap-1.5 py-3.5 px-4.5 bg-zinc-900/30 border border-zinc-800/40 backdrop-blur-md rounded-2xl rounded-tl-none">
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce shadow-[0_0_8px_rgba(129,140,248,0.5)] [animation-delay:-0.3s]" />
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce shadow-[0_0_8px_rgba(129,140,248,0.5)] [animation-delay:-0.15s]" />
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce shadow-[0_0_8px_rgba(129,140,248,0.5)]" />
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Chat Form Area */}
      <div className="p-4 border-t border-zinc-900 bg-zinc-950/60 backdrop-blur-md z-10">
        <div className="max-w-3xl mx-auto">
          <ChatInput onSend={onSendMessage} disabled={loading} />
          <div className="text-[10px] text-zinc-550 text-center mt-2.5 select-none tracking-wide">
            Answers are grounded strictly in SEC filings. Sourced references can be inspected in the citation details.
          </div>
        </div>
      </div>

    </div>
  );
}
