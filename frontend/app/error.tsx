"use client";

export default function Error({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
      <h2 className="text-2xl font-bold text-red-400">오류가 발생했습니다</h2>
      <p className="text-slate-400">{error.message}</p>
      <button onClick={reset} className="btn-primary">
        다시 시도
      </button>
    </div>
  );
}
