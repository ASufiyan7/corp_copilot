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
    <div className="flex-1 flex flex-col bg-zinc-950/20 text-white overflow-hidden">
      
      {/* Thread Chat Header */}
      <div className="h-16 flex-shrink-0 flex items-center px-6 border-b border-zinc-900 bg-zinc-950/40 backdrop-blur-md">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-indigo-400" />
          <h2 className="text-sm font-semibold text-white truncate max-w-lg">
            {threadTitle || "Research Conversation"}
          </h2>
        </div>
      </div>

      {/* Message History Scrolling Container */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin"
      >
        {messages.length === 0 ? (
          /* Empty/Welcome State showing Sample Prompts */
          <div className="max-w-2xl mx-auto py-12 flex flex-col items-center">
            
            <div className="w-12 h-12 flex items-center justify-center bg-indigo-500/10 text-indigo-400 rounded-xl mb-4">
              <Compass className="w-6 h-6 animate-pulse" />
            </div>
            
            <h2 className="text-xl font-bold tracking-tight text-white mb-2">
              SEC Filing Intelligence Copilot
            </h2>
            <p className="text-sm text-zinc-400 text-center max-w-md mb-8">
              Ask a question about S&P 500 company filings. Document Copilot will fetch the filings, extract citations, and construct grounded answers.
            </p>

            <div className="grid gap-3.5 sm:grid-cols-2 w-full">
              {SAMPLE_PROMPTS.map((prompt, idx) => (
                <div
                  key={idx}
                  onClick={() => onSendMessage(prompt.text)}
                  className="group p-4 bg-zinc-900/30 hover:bg-zinc-900/60 border border-zinc-900 hover:border-zinc-800/80 rounded-xl cursor-pointer text-left transition-all duration-200"
                >
                  <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-400 mb-1 group-hover:text-indigo-300">
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
            
            {/* Loading/Reponding Indicator bubble */}
            {loading && messages[messages.length - 1]?.role === "user" && (
              <div className="flex gap-4 w-full justify-start items-center">
                <div className="w-8.5 h-8.5 flex-shrink-0 flex items-center justify-center bg-gradient-to-tr from-indigo-500 to-violet-600 text-white rounded-lg shadow-md">
                  <Cpu className="w-4 h-4" />
                </div>
                <div className="flex items-center gap-1.5 py-3 px-4 bg-zinc-950/30 border border-zinc-900 rounded-2xl">
                  <span className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce delay-100" />
                  <span className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce delay-200" />
                  <span className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce delay-300" />
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Chat Form Area */}
      <div className="p-4 border-t border-zinc-900 bg-zinc-950/40 backdrop-blur-md">
        <div className="max-w-3xl mx-auto">
          <ChatInput onSend={onSendMessage} disabled={loading} />
          <div className="text-[10px] text-zinc-500 text-center mt-2">
            Answers are grounded strictly in SEC filings. Sourced references can be inspected in the citation details.
          </div>
        </div>
      </div>

    </div>
  );
}
