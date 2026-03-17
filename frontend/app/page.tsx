import ChatInput from "@/components/chat/ChatInput";
import SuggestedPrompts from "@/components/chat/SuggestedPrompts";

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-8rem)]">
      <div className="text-center mb-12">
        <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
          PC Build Advisor
        </h1>
        <p className="text-xl text-slate-400">
          AI가 분석하는 맞춤형 PC 견적 추천
        </p>
      </div>

      <div className="w-full max-w-2xl">
        <p className="text-center text-slate-400 mb-6 text-lg">
          어떤 PC가 필요하신가요?
        </p>
        <ChatInput />
        <SuggestedPrompts />
      </div>

      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-4xl">
        {[
          { icon: "🎯", title: "자연어 분석", desc: "게임명, 용도, 예산을 자유롭게 입력" },
          { icon: "⚡", title: "3단계 견적", desc: "최소/균형/최고 세 가지 옵션 제공" },
          { icon: "✅", title: "호환성 검증", desc: "CPU/GPU/메모리 등 자동 호환성 확인" },
        ].map((feature) => (
          <div key={feature.title} className="card text-center">
            <div className="text-3xl mb-3">{feature.icon}</div>
            <h3 className="font-semibold mb-2">{feature.title}</h3>
            <p className="text-slate-400 text-sm">{feature.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
