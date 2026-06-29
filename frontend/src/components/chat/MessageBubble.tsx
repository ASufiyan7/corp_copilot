"use client";

import React from "react";
import { User, Cpu } from "lucide-react";
import { Message } from "../../hooks/useMessages";
import CitationCard from "./CitationCard";

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-4.5 w-full animate-fade-in-up ${isUser ? "justify-end" : "justify-start"}`}>
      
      {/* Assistant Avatar Left */}
      {!isUser && (
        <div className="w-9 h-9 flex-shrink-0 flex items-center justify-center bg-gradient-to-tr from-indigo-500 to-violet-600 text-white rounded-xl shadow-lg shadow-indigo-500/20 hover:scale-105 transition-all duration-300">
          <Cpu className="w-4.5 h-4.5" />
        </div>
      )}

      {/* Message Content Bubble */}
      <div className="max-w-[85%] flex flex-col gap-2.5">
        <div
          className={`px-5 py-3.5 rounded-2xl shadow-md leading-relaxed text-sm transition-all duration-300 ${
            isUser
              ? "bg-zinc-900 border border-zinc-800/80 text-zinc-100 rounded-tr-none"
              : "glass-card border-zinc-900/60 hover:border-zinc-800/60 text-zinc-200 rounded-tl-none font-sans"
          }`}
        >
          {/* Main Content */}
          <div className="whitespace-pre-line select-text leading-relaxed">
            {message.content}
          </div>
          
          {/* Timestamp */}
          <div className="text-[9px] text-zinc-550 mt-2.5 text-right select-none tracking-wide">
            {new Date(message.created_at).toLocaleTimeString(undefined, {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </div>
        </div>

        {/* Citations Footer Section */}
        {!isUser && message.citations && message.citations.length > 0 && (
          <div className="mt-1 space-y-2 animate-fade-in-up [animation-delay:150ms]">
            <span className="block text-[10px] font-bold uppercase tracking-widest text-zinc-550 pl-1.5">
              Grounded Citations ({message.citations.length})
            </span>
            <div className="grid gap-3 sm:grid-cols-1 md:grid-cols-2">
              {message.citations.map((citation, idx) => (
                <CitationCard key={idx} citation={citation} />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* User Avatar Right */}
      {isUser && (
        <div className="w-9 h-9 flex-shrink-0 flex items-center justify-center bg-zinc-900 border border-zinc-800/80 text-zinc-350 rounded-xl shadow-md hover:scale-105 transition-all duration-300">
          <User className="w-4.5 h-4.5" />
        </div>
      )}

    </div>
  );
}
