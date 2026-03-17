"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import QuoteTabs from "@/components/quote/QuoteTabs";
import { apiClient } from "@/lib/api-client";

export default function QuoteDetailPage() {
  const { id } = useParams<{ id: string }>();

  const { data: quote, isLoading, error } = useQuery({
    queryKey: ["quote", id],
    queryFn: () => apiClient.get(`/quotes/${id}`).then((r) => r.data),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-400">견적을 생성하고 있습니다...</p>
        </div>
      </div>
    );
  }

  if (error || !quote) {
    return (
      <div className="text-center py-20">
        <p className="text-red-400">견적을 불러올 수 없습니다.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">PC 견적 결과</h1>
        <p className="text-slate-400">"{quote.user_input}"</p>
      </div>
      <QuoteTabs quote={quote} />
    </div>
  );
}
