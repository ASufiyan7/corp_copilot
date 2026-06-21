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
    <div className={`flex gap-4 w-full ${isUser ? "justify-end" : "justify-start"}`}>
      
      {/* Assistant Avatar Left */}
      {!isUser && (
        <div className="w-8.5 h-8.5 flex-shrink-0 flex items-center justify-center bg-gradient-to-tr from-indigo-500 to-violet-600 text-white rounded-lg shadow-md shadow-indigo-500/10">
          <Cpu className="w-4 h-4" />
        </div>
      )}

      {/* Message Content Bubble */}
      <div className={`max-w-[85%] flex flex-col gap-2`}>
        <div
          className={`px-4.5 py-3 rounded-2xl shadow-sm leading-relaxed text-sm ${
            isUser
              ? "bg-zinc-800 text-white rounded-tr-sm"
              : "bg-zinc-950/50 border border-zinc-900 text-zinc-150 rounded-tl-sm font-sans"
          }`}
        >
          {/* Main Content */}
          <div className="whitespace-pre-line select-text">
            {message.content}
          </div>
          
          {/* Timestamp */}
          <div className="text-[10px] text-zinc-500 mt-2 text-right select-none">
            {new Date(message.created_at).toLocaleTimeString(undefined, {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </div>
        </div>

        {/* Citations Footer Section */}
        {!isUser && message.citations && message.citations.length > 0 && (
          <div className="mt-2 space-y-2">
            <span className="block text-[10px] font-bold uppercase tracking-wider text-zinc-500 pl-1">
              Grounded Citations ({message.citations.length})
            </span>
            <div className="grid gap-2 sm:grid-cols-1 md:grid-cols-2">
              {message.citations.map((citation, idx) => (
                <CitationCard key={idx} citation={citation} />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* User Avatar Right */}
      {isUser && (
        <div className="w-8.5 h-8.5 flex-shrink-0 flex items-center justify-center bg-zinc-850 border border-zinc-850 text-zinc-300 rounded-lg">
          <User className="w-4 h-4" />
        </div>
      )}

    </div>
  );
}
