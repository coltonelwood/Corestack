import { Suspense } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { StatusDot } from "@/components/ui/status-dot";
import { EmptyState } from "@/components/state/empty";
import { StatusFilter } from "@/components/ui/status-filter";
import { formatDateTime } from "@/lib/utils";
import { getWorkflowRuns } from "@/app/actions/workflows";
import Link from "next/link";
import { ChevronRight, Zap, Coins, Hash } from "lucide-react";

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

interface Props {
  searchParams: Promise<{ status?: string }>;
}

export default async function WorkflowsPage({ searchParams }: Props) {
  const params = await searchParams;
  let allWorkflows: Awaited<ReturnType<typeof getWorkflowRuns>> = [];
  try {
    allWorkflows = await getWorkflowRuns();
  } catch {
    // Table may not exist yet
  }

  const workflows = params.status
    ? allWorkflows.filter((w) => w.status === params.status)
    : allWorkflows;

  const counts = {
    all: allWorkflows.length,
    running: allWorkflows.filter((w) => w.status === "running").length,
    paused: allWorkflows.filter((w) => w.status === "paused").length,
    completed: allWorkflows.filter((w) => w.status === "completed").length,
    failed: allWorkflows.filter((w) => w.status === "failed").length,
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Workflows"
        description="Product launch workflows and automation pipelines."
        badge={counts.all > 0 ? <Badge variant="secondary">{counts.all}</Badge> : undefined}
      />

      {counts.all > 0 && (
        <Suspense>
          <StatusFilter
            options={[
              { label: "All", value: "", count: counts.all },
              { label: "Running", value: "running", count: counts.running },
              { label: "Awaiting", value: "paused", count: counts.paused },
              { label: "Completed", value: "completed", count: counts.completed },
              { label: "Failed", value: "failed", count: counts.failed },
            ]}
          />
        </Suspense>
      )}

      {workflows.length === 0 ? (
        <Card>
          <CardContent className="p-0">
            <EmptyState
              title={params.status ? `No ${statusLabel[params.status] ?? params.status} workflows` : "No workflows yet"}
              description="Launch a product to trigger the first workflow."
            />
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {workflows.map((wf) => {
            const pct = wf.total_steps > 0 ? Math.round((wf.completed_steps / wf.total_steps) * 100) : 0;

            return (
              <Link key={wf.id} href={`/dashboard/workflows/${wf.id}`}>
                <Card className="hover:border-primary/30 transition-colors cursor-pointer">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between gap-4">
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                          <Zap className="h-4 w-4 text-primary" />
                        </div>
                        <div className="min-w-0">
                          <p className="font-medium truncate">{wf.name}</p>
                          <div className="flex items-center gap-3 text-xs text-muted-foreground mt-0.5">
                            <span>{wf.workflow_type}</span>
                            <span>&middot;</span>
                            <span className="tabular-nums">{formatDateTime(wf.created_at)}</span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-4 shrink-0">
                        <div className="hidden sm:flex items-center gap-4 text-xs text-muted-foreground">
                          <span className="flex items-center gap-1 tabular-nums">
                            <Hash className="h-3 w-3" />
                            {wf.completed_steps}/{wf.total_steps}
                          </span>
                          <span className="flex items-center gap-1 tabular-nums">
                            <Coins className="h-3 w-3" />
                            ${(wf.total_cost_cents / 100).toFixed(2)}
                          </span>
                        </div>

                        {/* Compact progress bar */}
                        <div className="hidden md:block w-20">
                          <div className="h-1.5 rounded-full bg-secondary overflow-hidden">
                            <div
                              className={`h-full rounded-full transition-all ${wf.status === "failed" ? "bg-destructive" : "bg-primary"}`}
                              style={{ width: `${pct}%` }}
                            />
                          </div>
                        </div>

                        <Badge variant={statusVariant[wf.status] ?? "secondary"}>
                          <StatusDot status={wf.status} className="mr-1.5" />
                          {statusLabel[wf.status] ?? wf.status}
                        </Badge>
                        <ChevronRight className="h-4 w-4 text-muted-foreground" />
                      </div>
                    </div>

                    {wf.error_message && (
                      <p className="mt-2 text-xs text-destructive bg-destructive/10 rounded px-2 py-1 truncate">
                        {wf.error_message}
                      </p>
                    )}
                  </CardContent>
                </Card>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
