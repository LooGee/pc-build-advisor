"use client";

import { useState } from "react";
import { apiClient } from "@/lib/api-client";
import { useQuoteStore } from "@/stores/quoteStore";

export function useQuoteGeneration() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { addChatMessage } = useQuoteStore();

  const generateQuote = async (userInput: string) => {
    setIsLoading(true);
    setError(null);

    addChatMessage({ role: "user", content: userInput, timestamp: new Date() });

    try {
      const response = await apiClient.post("/api/v1/quotes/generate", {
        user_input: userInput,
        llm_provider: "claude",
      });

      addChatMessage({
        role: "assistant",
        content: `견적이 생성되었습니다! 3가지 옵션을 확인해보세요.`,
        timestamp: new Date(),
      });

      return response.data;
    } catch (err: any) {
      const message = err.response?.data?.detail || "견적 생성에 실패했습니다.";
      setError(message);
      addChatMessage({
        role: "assistant",
        content: `오류: ${message}`,
        timestamp: new Date(),
      });
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  return { generateQuote, isLoading, error };
}
