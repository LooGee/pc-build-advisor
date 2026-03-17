import Link from "next/link";
import { Cpu } from "lucide-react";

export default function Header() {
  return (
    <header className="bg-slate-800 border-b border-slate-700 sticky top-0 z-50">
      <div className="container mx-auto px-4 max-w-7xl">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="flex items-center gap-2 font-bold text-lg">
            <Cpu className="w-6 h-6 text-blue-400" />
            <span>PC Build Advisor</span>
          </Link>
          <nav className="flex items-center gap-6 text-sm">
            <Link href="/" className="text-slate-400 hover:text-white transition-colors">
              홈
            </Link>
            <Link href="/quotes" className="text-slate-400 hover:text-white transition-colors">
              내 견적
            </Link>
            <Link href="/components" className="text-slate-400 hover:text-white transition-colors">
              부품 카탈로그
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}
