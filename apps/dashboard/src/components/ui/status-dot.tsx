import { cn } from "@/lib/utils";

const colorMap: Record<string, string> = {
  active: "bg-emerald-500",
  running: "bg-emerald-500",
  completed: "bg-blue-500",
  approved: "bg-blue-500",
  paused: "bg-amber-500",
  pending: "bg-amber-500",
  queued: "bg-amber-500",
  draft: "bg-gray-400",
  setup: "bg-gray-400",
  idle: "bg-gray-400",
  failed: "bg-red-500",
  rejected: "bg-red-500",
  archived: "bg-gray-400",
  in_progress: "bg-emerald-500",
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
        "inline-block h-2 w-2 rounded-full",
        colorMap[status] ?? "bg-gray-400",
        className
      )}
    />
  );
}
