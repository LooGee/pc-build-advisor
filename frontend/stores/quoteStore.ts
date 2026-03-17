import { create } from "zustand";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface QuoteStore {
  chatHistory: ChatMessage[];
  currentQuoteId: string | null;
  addChatMessage: (message: ChatMessage) => void;
  setCurrentQuoteId: (id: string | null) => void;
  clearHistory: () => void;
}

export const useQuoteStore = create<QuoteStore>((set) => ({
  chatHistory: [],
  currentQuoteId: null,
  addChatMessage: (message) =>
    set((state) => ({ chatHistory: [...state.chatHistory, message] })),
  setCurrentQuoteId: (id) => set({ currentQuoteId: id }),
  clearHistory: () => set({ chatHistory: [], currentQuoteId: null }),
}));
