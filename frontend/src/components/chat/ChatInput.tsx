"use client";

import React, { useRef, useEffect } from "react";
import { Send, Loader2 } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled: boolean;
  placeholder?: string;
}

export default function ChatInput({ onSend, disabled, placeholder }: ChatInputProps) {
  const [text, setText] = React.useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea heights
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  }, [text]);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!text.trim() || disabled) return;
    onSend(text.trim());
    setText("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative flex items-end gap-3 bg-zinc-950/40 border border-zinc-900 rounded-xl p-2.5 focus-within:border-zinc-800 transition-all duration-200">
      <textarea
        ref={textareaRef}
        rows={1}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder || "Ask a question about Apple, Microsoft, NVIDIA, Amazon or Alphabet filings..."}
        className="flex-1 max-h-48 min-h-[24px] px-3 py-1.5 bg-transparent text-white placeholder-zinc-500 text-sm focus:outline-none resize-none overflow-y-auto leading-relaxed scrollbar-thin"
        disabled={disabled}
      />
      
      <button
        type="submit"
        disabled={!text.trim() || disabled}
        className="p-2.5 bg-gradient-to-tr from-indigo-500 to-violet-600 disabled:from-zinc-900 disabled:to-zinc-900 text-white disabled:text-zinc-600 rounded-lg shadow-md transition-all duration-200 disabled:opacity-50 disabled:shadow-none flex-shrink-0"
      >
        {disabled ? (
          <Loader2 className="w-4.5 h-4.5 animate-spin" />
        ) : (
          <Send className="w-4.5 h-4.5" />
        )}
      </button>
    </form>
  );
}
