import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";
import Header from "@/components/common/Header";

export const metadata: Metadata = {
  title: "PC Build Advisor - AI PC 견적 추천",
  description: "AI가 분석하는 맞춤형 PC 견적 추천 서비스",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko" className="dark">
      <body className="min-h-screen bg-slate-900 text-slate-100">
        <Providers>
          <Header />
          <main className="container mx-auto px-4 py-8 max-w-7xl">
            {children}
          </main>
        </Providers>
      </body>
    </html>
  );
}
