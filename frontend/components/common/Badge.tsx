import { clsx } from "clsx";

type BadgeVariant = "ok" | "warning" | "error" | "info";

interface BadgeProps {
  variant: BadgeVariant;
  children: React.ReactNode;
}

const variantStyles: Record<BadgeVariant, string> = {
  ok: "bg-green-900/50 text-green-400 border-green-700",
  warning: "bg-yellow-900/50 text-yellow-400 border-yellow-700",
  error: "bg-red-900/50 text-red-400 border-red-700",
  info: "bg-blue-900/50 text-blue-400 border-blue-700",
};

export default function Badge({ variant, children }: BadgeProps) {
  return (
    <span
      className={clsx(
        "inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border",
        variantStyles[variant]
      )}
    >
      {children}
    </span>
  );
}
