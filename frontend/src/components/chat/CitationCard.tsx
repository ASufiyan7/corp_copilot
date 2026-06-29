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

  const getTickerDetails = (ticker?: string) => {
    const t = ticker?.toUpperCase() || "";
    if (t.includes("AAPL")) {
      return {
        badgeBg: "bg-zinc-200/10 border-zinc-800 text-zinc-300",
        border: "hover:border-zinc-500/30",
        iconColor: "text-zinc-400",
        iconBg: "bg-zinc-100/5",
        accent: "border-zinc-500/40",
      };
    }
    if (t.includes("MSFT")) {
      return {
        badgeBg: "bg-blue-500/10 border-blue-500/20 text-blue-300",
        border: "hover:border-blue-500/30",
        iconColor: "text-blue-400",
        iconBg: "bg-blue-500/10",
        accent: "border-blue-500/40",
      };
    }
    if (t.includes("NVDA")) {
      return {
        badgeBg: "bg-emerald-500/10 border-emerald-500/20 text-emerald-300",
        border: "hover:border-emerald-500/30",
        iconColor: "text-emerald-400",
        iconBg: "bg-emerald-500/10",
        accent: "border-emerald-500/40",
      };
    }
    if (t.includes("AMZN")) {
      return {
        badgeBg: "bg-amber-500/10 border-amber-500/20 text-amber-300",
        border: "hover:border-amber-500/30",
        iconColor: "text-amber-400",
        iconBg: "bg-amber-500/10",
        accent: "border-amber-500/40",
      };
    }
    if (t.includes("GOOG") || t.includes("GOOGL") || t.includes("ALPH")) {
      return {
        badgeBg: "bg-red-500/10 border-red-500/20 text-red-300",
        border: "hover:border-red-500/30",
        iconColor: "text-red-400",
        iconBg: "bg-red-500/10",
        accent: "border-red-500/40",
      };
    }
    return {
      badgeBg: "bg-indigo-500/10 border-indigo-500/20 text-indigo-300",
      border: "hover:border-indigo-500/30",
      iconColor: "text-indigo-400",
      iconBg: "bg-indigo-500/10",
      accent: "border-indigo-500/40",
    };
  };

  const theme = getTickerDetails(citation.ticker);

  return (
    <div className={`glass-card rounded-2xl overflow-hidden ${theme.border} transition-all duration-300 shadow-md shadow-black/5`}>
      
      {/* Citation Header Summary */}
      <div
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between p-3 cursor-pointer hover:bg-zinc-900/30 select-none transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 flex items-center justify-center rounded-xl shadow-inner ${theme.iconBg} ${theme.iconColor} transition-transform duration-250 ${expanded ? "scale-95" : ""}`}>
            <BookOpen className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-white uppercase tracking-wider">
                {citation.ticker || "SEC"}
              </span>
              <span className={`text-[9px] px-2 py-0.5 rounded-md font-bold uppercase tracking-wide border ${theme.badgeBg}`}>
                {citation.filing_type || "Filing"}
              </span>
            </div>
            {citation.filing_date && (
              <span className="text-[10px] text-zinc-500 font-medium">
                Filing Date: {formatDate(citation.filing_date)}
              </span>
            )}
          </div>
        </div>
        
        <div className="text-zinc-500 hover:text-zinc-300 p-1">
          {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </div>

      {/* Expanded Text Excerpt Area */}
      {expanded && (
        <div className="px-4 pb-4 pt-2 border-t border-zinc-900 bg-zinc-950/40 animate-fade-in-up">
          <span className="block text-[9px] uppercase font-bold tracking-widest text-zinc-500 mb-2">
            Retrieved Supporting Passage
          </span>
          <p className={`text-zinc-300 text-xs leading-relaxed font-sans pl-3 border-l-2 ${theme.accent} whitespace-pre-line italic bg-zinc-900/30 p-2.5 rounded-r-xl`}>
            "{citation.excerpt}"
          </p>
        </div>
      )}

    </div>
  );
}
