"use client";

import { useQuoteStore } from "@/stores/quoteStore";
import ChatBubble from "./ChatBubble";

export default function ChatHistory() {
  const { chatHistory } = useQuoteStore();

  if (chatHistory.length === 0) {
    return (
      <div className="flex items-center justify-center py-20 text-slate-500">
        <p>대화를 시작해보세요!</p>
      </div>
    );
  }

  return (
    <div className="space-y-2 p-4">
      {chatHistory.map((msg, i) => (
        <ChatBubble key={i} role={msg.role} content={msg.content} timestamp={msg.timestamp} />
      ))}
    </div>
  );
}
