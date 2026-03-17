import { CheckCircle, AlertTriangle, XCircle, Info } from "lucide-react";

type Status = "ok" | "warning" | "error" | "info";

const CONFIG: Record<Status, { icon: React.ReactNode; label: string; className: string }> = {
  ok: { icon: <CheckCircle className="w-4 h-4" />, label: "호환", className: "text-green-400" },
  warning: { icon: <AlertTriangle className="w-4 h-4" />, label: "주의", className: "text-yellow-400" },
  error: { icon: <XCircle className="w-4 h-4" />, label: "비호환", className: "text-red-400" },
  info: { icon: <Info className="w-4 h-4" />, label: "정보", className: "text-blue-400" },
};

export default function CompatibilityBadge({ status }: { status: Status }) {
  const config = CONFIG[status];
  return (
    <span className={`flex items-center gap-1 text-xs ${config.className}`}>
      {config.icon}
      {config.label}
    </span>
  );
}
