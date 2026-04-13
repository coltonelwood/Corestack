import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { StatusDot } from "@/components/ui/status-dot";
import { EmptyState } from "@/components/state/empty";
import { formatDateTime } from "@/lib/utils";
import { getWorkflowRuns } from "@/app/actions/workflows";
import Link from "next/link";
import { ChevronRight, Zap, Clock, Coins, Hash } from "lucide-react";

const statusVariant: Record<string, "success" | "warning" | "destructive" | "secondary" | "default"> = {
  running: "default",
  paused: "warning",
  completed: "success",
  failed: "destructive",
  cancelled: "secondary",
};

const statusLabel: Record<string, string> = {
  running: "Running",
  paused: "Awaiting Approval",
  completed: "Completed",
  failed: "Failed",
  cancelled: "Cancelled",
};

export default async function WorkflowsPage() {
  let workflows: Awaited<ReturnType<typeof getWorkflowRuns>> = [];
  try {
    workflows = await getWorkflowRuns();
  } catch {
    // Table may not exist yet — show empty state
  }

  const runningCount = workflows.filter((w) => w.status === "running" || w.status === "paused").length;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Workflows"
        description={
          runningCount > 0
            ? `${runningCount} workflow${runningCount !== 1 ? "s" : ""} in progress.`
            : "Product launch workflows and automation pipelines."
        }
      />

      {workflows.length === 0 ? (
        <Card>
          <CardContent className="p-0">
            <EmptyState
              title="No workflows yet"
              description="Launch a product to trigger the first workflow. Workflows orchestrate agents through multi-step pipelines with approval gates."
            />
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {workflows.map((wf) => (
            <Link key={wf.id} href={`/dashboard/workflows/${wf.id}`}>
              <Card className="hover:border-primary/30 transition-colors cursor-pointer">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3">
                        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
                          <Zap className="h-4 w-4 text-primary" />
                        </div>
                        <div>
                          <p className="font-medium">{wf.name}</p>
                          <p className="text-xs text-muted-foreground">
                            {wf.workflow_type} &middot; {formatDateTime(wf.created_at)}
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-4">
                      <div className="hidden sm:flex items-center gap-4 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Hash className="h-3 w-3" />
                          {wf.completed_steps}/{wf.total_steps} steps
                        </span>
                        <span className="flex items-center gap-1">
                          <Coins className="h-3 w-3" />
                          ${(wf.total_cost_cents / 100).toFixed(2)}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {wf.total_tokens.toLocaleString()} tokens
                        </span>
                      </div>
                      <Badge variant={statusVariant[wf.status] ?? "secondary"}>
                        <StatusDot status={wf.status} className="mr-1.5" />
                        {statusLabel[wf.status] ?? wf.status}
                      </Badge>
                      <ChevronRight className="h-4 w-4 text-muted-foreground" />
                    </div>
                  </div>

                  {wf.error_message && (
                    <p className="mt-2 text-xs text-destructive bg-destructive/10 rounded px-2 py-1">
                      {wf.error_message}
                    </p>
                  )}
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
