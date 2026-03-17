"use client";

import { useState } from "react";
import { RefreshCw, CheckCircle, AlertTriangle, XCircle } from "lucide-react";
import PriceComparison from "@/components/price/PriceComparison";

interface QuoteCardProps {
  quoteData: any;
}

const CATEGORY_LABELS: Record<string, string> = {
  cpu: "CPU",
  gpu: "그래픽카드 (GPU)",
  motherboard: "메인보드",
  ram: "RAM",
  storage: "저장장치",
  psu: "파워서플라이",
  case: "케이스",
  cooler: "CPU 쿨러",
};

function CompatibilityIcon({ status }: { status: string }) {
  if (status === "ok") return <CheckCircle className="w-4 h-4 text-green-400 shrink-0" />;
  if (status === "warning") return <AlertTriangle className="w-4 h-4 text-yellow-400 shrink-0" />;
  return <XCircle className="w-4 h-4 text-red-400 shrink-0" />;
}

export default function QuoteCard({ quoteData }: QuoteCardProps) {
  const [expandedComponent, setExpandedComponent] = useState<string | null>(null);

  return (
    <div className="space-y-4">
      {/* Summary */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold">{quoteData.tier_name}</h2>
            <p className="text-slate-400 text-sm">{quoteData.tier_description}</p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-blue-400">
              ₩{quoteData.total_price_krw?.toLocaleString()}
            </p>
            <p className="text-slate-500 text-xs">배송비 포함</p>
          </div>
        </div>

        {/* Performance estimates */}
        {quoteData.estimated_performance && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4">
            {quoteData.estimated_performance.estimated_gaming_fps_1080p && (
              <div className="bg-slate-700 rounded-lg p-3 text-center">
                <p className="text-xs text-slate-400">1080p FPS</p>
                <p className="text-lg font-bold text-green-400">
                  {quoteData.estimated_performance.estimated_gaming_fps_1080p}
                </p>
              </div>
            )}
            {quoteData.estimated_performance.estimated_gaming_fps_1440p && (
              <div className="bg-slate-700 rounded-lg p-3 text-center">
                <p className="text-xs text-slate-400">1440p FPS</p>
                <p className="text-lg font-bold text-blue-400">
                  {quoteData.estimated_performance.estimated_gaming_fps_1440p}
                </p>
              </div>
            )}
            {quoteData.estimated_performance.estimated_power_consumption_w && (
              <div className="bg-slate-700 rounded-lg p-3 text-center">
                <p className="text-xs text-slate-400">소비전력</p>
                <p className="text-lg font-bold text-yellow-400">
                  {quoteData.estimated_performance.estimated_power_consumption_w}W
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Component List */}
      <div className="space-y-2">
        {quoteData.components?.map((component: any) => (
          <div key={component.id} className="card">
            <div
              className="flex items-center justify-between cursor-pointer"
              onClick={() => setExpandedComponent(expandedComponent === component.id ? null : component.id)}
            >
              <div className="flex items-center gap-3 flex-1 min-w-0">
                <CompatibilityIcon status={component.compatibility_status} />
                <div className="min-w-0">
                  <p className="text-xs text-slate-500 uppercase tracking-wide">
                    {CATEGORY_LABELS[component.category] || component.category}
                  </p>
                  <p className="font-medium text-sm truncate">
                    {component.brand} {component.model}
                  </p>
                </div>
              </div>
              <div className="text-right ml-4 shrink-0">
                <p className="font-semibold">
                  ₩{component.price_info?.price_krw?.toLocaleString()}
                </p>
                <p className="text-xs text-slate-500">
                  {component.price_info?.sources?.[0]?.source}
                </p>
              </div>
            </div>

            {/* Expanded: Price comparison */}
            {expandedComponent === component.id && component.price_info?.sources?.length > 0 && (
              <div className="mt-3 pt-3 border-t border-slate-700">
                <PriceComparison sources={component.price_info.sources} />
                {component.compatibility_notes && (
                  <p className="text-xs text-yellow-400 mt-2">
                    ⚠️ {component.compatibility_notes}
                  </p>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Compatibility Issues */}
      {quoteData.compatibility?.issues?.length > 0 && (
        <div className="card border-yellow-700">
          <h3 className="font-semibold mb-3 text-yellow-400">호환성 주의사항</h3>
          <ul className="space-y-2">
            {quoteData.compatibility.issues.map((issue: any, i: number) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <span>{issue.icon || "⚠️"}</span>
                <div>
                  <p className="font-medium">{issue.title_ko}</p>
                  <p className="text-slate-400">{issue.message_ko}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        <button className="btn-primary flex-1">구매 링크 보기</button>
        <button className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm transition-colors">
          <RefreshCw className="w-4 h-4" />
          부품 교체
        </button>
      </div>
    </div>
  );
}
