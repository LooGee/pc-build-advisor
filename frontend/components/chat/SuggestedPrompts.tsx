"use client";

import { useRouter } from "next/navigation";
import { useQuoteGeneration } from "@/hooks/useQuoteGeneration";

const SUGGESTED_PROMPTS = [
  { icon: "🎮", label: "배그 고사양 150만원", prompt: "배틀그라운드를 고사양으로 돌리고 싶어요. 예산 150만원" },
  { icon: "🎬", label: "영상편집 200만원", prompt: "4K 영상편집 작업용 PC가 필요합니다. 예산 200만원" },
  { icon: "💻", label: "사무용 100만원", prompt: "인터넷, 오피스 작업용 가성비 사무용 PC. 예산 100만원" },
  { icon: "🖥️", label: "4K 게이밍 250만원", prompt: "사이버펑크 4K 울트라로 돌리고 싶어요. 예산 250만원" },
];

export default function SuggestedPrompts() {
  const router = useRouter();
  const { generateQuote, isLoading } = useQuoteGeneration();

  const handleClick = async (prompt: string) => {
    if (isLoading) return;
    const result = await generateQuote(prompt);
    if (result?.id) {
      router.push(`/quotes/${result.id}`);
    }
  };

  return (
    <div className="mt-4 flex flex-wrap gap-2 justify-center">
      {SUGGESTED_PROMPTS.map((item) => (
        <button
          key={item.label}
          onClick={() => handleClick(item.prompt)}
          disabled={isLoading}
          className="flex items-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded-full text-sm text-slate-300 transition-colors disabled:opacity-50"
        >
          <span>{item.icon}</span>
          <span>{item.label}</span>
        </button>
      ))}
    </div>
  );
}
