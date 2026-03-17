"use client";

import { Suspense } from "react";
import ChatHistory from "@/components/chat/ChatHistory";
import ChatInput from "@/components/chat/ChatInput";

export default function ChatPage() {
  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <div className="flex-1 overflow-y-auto">
        <Suspense fallback={<div className="text-slate-400">로딩 중...</div>}>
          <ChatHistory />
        </Suspense>
      </div>
      <div className="sticky bottom-0 bg-slate-900 pt-4 pb-4">
        <ChatInput />
      </div>
    </div>
  );
}
