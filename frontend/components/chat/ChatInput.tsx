"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Send, Loader2 } from "lucide-react";
import { useQuoteGeneration } from "@/hooks/useQuoteGeneration";

export default function ChatInput() {
  const [input, setInput] = useState("");
  const router = useRouter();
  const { generateQuote, isLoading } = useQuoteGeneration();

  const handleSubmit = async (text?: string) => {
    const query = text || input;
    if (!query.trim() || isLoading) return;

    setInput("");
    const result = await generateQuote(query);
    if (result?.id) {
      router.push(`/quotes/${result.id}`);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="relative">
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="예: 배틀그라운드를 고사양으로 돌리고 싶어요. 예산은 150만원입니다."
        className="w-full bg-slate-800 border border-slate-600 rounded-xl py-4 pl-4 pr-14 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none min-h-[60px] max-h-[160px]"
        rows={2}
        disabled={isLoading}
      />
      <button
        onClick={() => handleSubmit()}
        disabled={!input.trim() || isLoading}
        className="absolute right-3 bottom-3 p-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed rounded-lg transition-colors"
      >
        {isLoading ? (
          <Loader2 className="w-5 h-5 animate-spin text-white" />
        ) : (
          <Send className="w-5 h-5 text-white" />
        )}
      </button>
    </div>
  );
}
