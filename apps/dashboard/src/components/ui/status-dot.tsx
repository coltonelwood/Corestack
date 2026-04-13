import { cn } from "@/lib/utils";

const colorMap: Record<string, string> = {
  active: "bg-emerald-500",
  running: "bg-emerald-500 animate-pulse-dot",
  completed: "bg-emerald-500",
  approved: "bg-emerald-500",
  paused: "bg-amber-500",
  pending: "bg-amber-500 animate-pulse-dot",
  queued: "bg-amber-500 animate-pulse-dot",
  draft: "bg-gray-400",
  setup: "bg-gray-400",
  idle: "bg-gray-400",
  failed: "bg-red-500",
  rejected: "bg-red-500",
  archived: "bg-gray-400",
  in_progress: "bg-blue-500 animate-pulse-dot",
  waiting_approval: "bg-amber-500 animate-pulse-dot",
  low: "bg-gray-400",
  medium: "bg-amber-500",
  high: "bg-orange-500",
  critical: "bg-red-500",
};

interface StatusDotProps {
  status: string;
  className?: string;
}

export function StatusDot({ status, className }: StatusDotProps) {
  return (
    <span
      className={cn(
        "inline-block h-2 w-2 rounded-full shrink-0",
        colorMap[status] ?? "bg-gray-400",
        className
      )}
    />
  );
}
