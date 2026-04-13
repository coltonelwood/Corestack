"use client";

import { ErrorState } from "@/components/state/error";

export default function DashboardError({
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return <ErrorState message="Failed to load dashboard data." retry={reset} />;
}
