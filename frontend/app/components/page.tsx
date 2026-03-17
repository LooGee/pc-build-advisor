"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { COMPONENT_CATEGORIES } from "@/lib/constants";

export default function ComponentsPage() {
  const [selectedCategory, setSelectedCategory] = useState("gpu");

  const { data, isLoading } = useQuery({
    queryKey: ["components", selectedCategory],
    queryFn: () =>
      apiClient.get(`/api/v1/components?category=${selectedCategory}&limit=20`).then((r) => r.data),
  });

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">부품 카탈로그</h1>

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2 mb-6">
        {COMPONENT_CATEGORIES.map((cat) => (
          <button
            key={cat.key}
            onClick={() => setSelectedCategory(cat.key)}
            className={`px-3 py-1.5 rounded-full text-sm transition-colors ${
              selectedCategory === cat.key
                ? "bg-blue-600 text-white"
                : "bg-slate-700 text-slate-300 hover:bg-slate-600"
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Component List */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-4 bg-slate-700 rounded w-3/4 mb-3" />
              <div className="h-3 bg-slate-700 rounded w-1/2 mb-4" />
              <div className="h-6 bg-slate-700 rounded w-1/3" />
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data?.items?.map((component: any) => (
            <div key={component.id} className="card hover:border-slate-500 transition-colors cursor-pointer">
              <div>
                <p className="text-xs text-slate-500 uppercase mb-1">{component.brand}</p>
                <h3 className="font-semibold text-sm">{component.model}</h3>
              </div>
              <div className="mt-3">
                {component.min_price_krw && (
                  <p className="text-lg font-bold text-blue-400">
                    ₩{component.min_price_krw.toLocaleString()}~
                  </p>
                )}
                <p className="text-xs text-slate-500">
                  {component.prices?.length || 0}개 사이트 비교
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
