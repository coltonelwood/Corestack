"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { approveApproval, rejectApproval } from "@/app/actions/approvals";

export function ApprovalActions({ id }: { id: string }) {
  const router = useRouter();
  const [pending, setPending] = useState<"approve" | "reject" | null>(null);

  async function handleApprove() {
    setPending("approve");
    await approveApproval(id);
    router.refresh();
  }

  async function handleReject() {
    setPending("reject");
    await rejectApproval(id);
    router.refresh();
  }

  return (
    <div className="flex items-center gap-1">
      <Button
        size="sm"
        variant="ghost"
        className="h-8 w-8 p-0 text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50"
        onClick={handleApprove}
        disabled={pending !== null}
      >
        {pending === "approve" ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <CheckCircle2 className="h-4 w-4" />
        )}
      </Button>
      <Button
        size="sm"
        variant="ghost"
        className="h-8 w-8 p-0 text-red-500 hover:text-red-600 hover:bg-red-50"
        onClick={handleReject}
        disabled={pending !== null}
      >
        {pending === "reject" ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <XCircle className="h-4 w-4" />
        )}
      </Button>
    </div>
  );
}
