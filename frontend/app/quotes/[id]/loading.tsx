export default function QuoteLoading() {
  return (
    <div className="space-y-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="card animate-pulse">
          <div className="h-4 bg-slate-700 rounded w-1/4 mb-4" />
          <div className="space-y-3">
            {[1, 2, 3, 4].map((j) => (
              <div key={j} className="h-12 bg-slate-700 rounded" />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
