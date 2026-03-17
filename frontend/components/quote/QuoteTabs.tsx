"use client";

import { useState } from "react";
import { clsx } from "clsx";
import QuoteCard from "./QuoteCard";

interface QuoteTabsProps {
  quote: any;
}

const TIER_CONFIG = {
  minimum: { label: "💰 최소", color: "text-green-400", borderColor: "border-green-400" },
  balanced: { label: "⚖️ 균형", color: "text-blue-400", borderColor: "border-blue-400" },
  maximum: { label: "⚡ 최고", color: "text-purple-400", borderColor: "border-purple-400" },
};

export default function QuoteTabs({ quote }: QuoteTabsProps) {
  const [activeTab, setActiveTab] = useState<string>(quote.quotes?.[0]?.tier || "minimum");

  const activeQuote = quote.quotes?.find((q: any) => q.tier === activeTab);

  return (
    <div>
      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-slate-700">
        {quote.quotes?.map((q: any) => {
          const config = TIER_CONFIG[q.tier as keyof typeof TIER_CONFIG];
          return (
            <button
              key={q.tier}
              onClick={() => setActiveTab(q.tier)}
              className={clsx(
                "px-4 py-3 text-sm font-medium transition-colors border-b-2 -mb-px",
                activeTab === q.tier
                  ? clsx(config.color, config.borderColor)
                  : "text-slate-400 border-transparent hover:text-slate-300"
              )}
            >
              {config?.label}
              <span className="ml-2 text-xs opacity-75">
                ₩{q.total_price_krw?.toLocaleString()}
              </span>
            </button>
          );
        })}
      </div>

      {/* Active Tab Content */}
      {activeQuote && <QuoteCard quoteData={activeQuote} />}
    </div>
  );
}
