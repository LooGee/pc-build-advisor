import { ExternalLink } from "lucide-react";

interface PriceSource {
  source: string;
  price_krw: number;
  url?: string;
  in_stock?: boolean;
  shipping?: string;
}

interface PriceComparisonProps {
  sources: PriceSource[];
}

const SOURCE_LABELS: Record<string, string> = {
  danawa: "다나와",
  compuzone: "컴퓨존",
  coupang: "쿠팡",
  pcpartpicker: "PCPartPicker",
};

const SOURCE_COLORS: Record<string, string> = {
  danawa: "text-blue-400",
  compuzone: "text-green-400",
  coupang: "text-orange-400",
  pcpartpicker: "text-purple-400",
};

export default function PriceComparison({ sources }: PriceComparisonProps) {
  const sorted = [...sources].sort((a, b) => a.price_krw - b.price_krw);

  return (
    <div className="space-y-2">
      <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">가격 비교</p>
      {sorted.map((source, i) => (
        <div key={source.source} className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-2">
            {i === 0 && <span className="text-xs text-green-400 font-medium">최저</span>}
            <span className={SOURCE_COLORS[source.source] || "text-slate-400"}>
              {SOURCE_LABELS[source.source] || source.source}
            </span>
            {source.shipping === "rocket" && (
              <span className="text-xs bg-orange-900/50 text-orange-400 px-1 rounded">로켓배송</span>
            )}
            {!source.in_stock && (
              <span className="text-xs text-red-400">품절</span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <span className="font-medium">₩{source.price_krw.toLocaleString()}</span>
            {source.url && (
              <a href={source.url} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="w-3 h-3 text-slate-500 hover:text-slate-300" />
              </a>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
