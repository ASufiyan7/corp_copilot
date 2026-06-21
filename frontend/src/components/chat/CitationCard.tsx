"use client";

import React, { useState } from "react";
import { BookOpen, ChevronDown, ChevronUp } from "lucide-react";
import { Citation } from "../../hooks/useMessages";

interface CitationCardProps {
  citation: Citation;
}

export default function CitationCard({ citation }: CitationCardProps) {
  const [expanded, setExpanded] = useState(false);

  // Formatting date string nicely
  const formatDate = (dateStr?: string) => {
    if (!dateStr) return "";
    try {
      return new Date(dateStr).toLocaleDateString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="bg-zinc-900/40 border border-zinc-800 rounded-xl overflow-hidden hover:border-zinc-700 transition-all duration-200">
      
      {/* Citation Header Summary */}
      <div
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between p-3.5 cursor-pointer hover:bg-zinc-900/20 select-none transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 flex items-center justify-center bg-indigo-500/10 text-indigo-400 rounded-lg">
            <BookOpen className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-white uppercase tracking-wide">
                {citation.ticker || "SEC"}
              </span>
              <span className="text-[10px] bg-zinc-800 text-zinc-400 px-1.5 py-0.5 rounded font-semibold">
                {citation.filing_type || "Filing"}
              </span>
            </div>
            {citation.filing_date && (
              <span className="text-xs text-zinc-500">
                Filing Date: {formatDate(citation.filing_date)}
              </span>
            )}
          </div>
        </div>
        
        <div className="text-zinc-500 hover:text-zinc-300">
          {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </div>

      {/* Expanded Text Excerpt Area */}
      {expanded && (
        <div className="px-4 pb-4 pt-1 border-t border-zinc-900 bg-zinc-950/40">
          <span className="block text-[10px] uppercase font-bold tracking-wider text-zinc-500 mb-2">
            Retrieved Supporting Passage
          </span>
          <p className="text-zinc-300 text-sm leading-relaxed font-serif pl-3 border-l-2 border-indigo-500/50 whitespace-pre-line italic">
            "{citation.excerpt}"
          </p>
        </div>
      )}

    </div>
  );
}
