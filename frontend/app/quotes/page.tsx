import Link from "next/link";

export default function QuotesPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">내 견적 히스토리</h1>
      <p className="text-slate-400">
        저장된 견적이 없습니다.{" "}
        <Link href="/" className="text-blue-400 hover:underline">
          새 견적 만들기
        </Link>
      </p>
    </div>
  );
}
