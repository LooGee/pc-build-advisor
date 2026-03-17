interface QuoteSummaryProps {
  totalPrice: number;
  tierName: string;
  description: string;
}

export default function QuoteSummary({ totalPrice, tierName, description }: QuoteSummaryProps) {
  return (
    <div className="card">
      <h2 className="text-xl font-bold">{tierName}</h2>
      <p className="text-slate-400 text-sm mt-1">{description}</p>
      <p className="text-3xl font-bold text-blue-400 mt-3">
        ₩{totalPrice.toLocaleString()}
      </p>
    </div>
  );
}
