import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { StatusDot } from "@/components/ui/status-dot";
import { EmptyState } from "@/components/state/empty";
import { formatDateTime, formatCurrency } from "@/lib/utils";
import { getWorkflowRun } from "@/app/actions/workflows";
import {
  CheckCircle2,
  XCircle,
  Clock,
  Loader2,
  ShieldAlert,
  SkipForward,
  Coins,
  Zap,
  Hash,
} from "lucide-react";

const stepStatusConfig: Record<string, { icon: typeof CheckCircle2; color: string; label: string }> = {
  completed: { icon: CheckCircle2, color: "text-emerald-600", label: "Completed" },
  running: { icon: Loader2, color: "text-blue-500", label: "Running" },
  failed: { icon: XCircle, color: "text-red-500", label: "Failed" },
  pending: { icon: Clock, color: "text-muted-foreground", label: "Pending" },
  waiting_approval: { icon: ShieldAlert, color: "text-amber-500", label: "Awaiting Approval" },
  skipped: { icon: SkipForward, color: "text-muted-foreground", label: "Skipped" },
};

const wfStatusVariant: Record<string, "success" | "warning" | "destructive" | "secondary" | "default"> = {
  running: "default",
  paused: "warning",
  completed: "success",
  failed: "destructive",
  cancelled: "secondary",
};

interface Props {
  params: Promise<{ id: string }>;
}

export default async function WorkflowDetailPage({ params }: Props) {
  const { id } = await params;

  let workflow: Awaited<ReturnType<typeof getWorkflowRun>>;
  try {
    workflow = await getWorkflowRun(id);
  } catch {
    return (
      <div className="space-y-6">
        <PageHeader title="Workflow" />
        <Card>
          <CardContent className="p-0">
            <EmptyState title="Workflow not found" description="This workflow run could not be loaded." />
          </CardContent>
        </Card>
      </div>
    );
  }

  const steps = (workflow.steps ?? []) as Array<{
    id: string;
    step_key: string;
    step_name: string;
    status: string;
    agent_name: string | null;
    tokens_used: number;
    cost_cents: number;
    duration_ms: number;
    error_message: string | null;
    approval_id: string | null;
    started_at: string | null;
    completed_at: string | null;
  }>;

  return (
    <div className="space-y-6">
      <PageHeader
        title={workflow.name}
        description={`${workflow.workflow_type} workflow`}
      >
        <Badge variant={wfStatusVariant[workflow.status] ?? "secondary"}>
          <StatusDot status={workflow.status} className="mr-1.5" />
          {workflow.status === "paused" ? "Awaiting Approval" : workflow.status}
        </Badge>
      </PageHeader>

      {/* Summary cards */}
      <div className="grid gap-4 sm:grid-cols-4">
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
              <Hash className="h-4 w-4 text-primary" />
            </div>
            <div>
              <p className="text-2xl font-bold">{workflow.completed_steps}/{workflow.total_steps}</p>
              <p className="text-xs text-muted-foreground">Steps completed</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
              <Zap className="h-4 w-4 text-primary" />
            </div>
            <div>
              <p className="text-2xl font-bold">{workflow.total_tokens.toLocaleString()}</p>
              <p className="text-xs text-muted-foreground">Tokens used</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
              <Coins className="h-4 w-4 text-primary" />
            </div>
            <div>
              <p className="text-2xl font-bold">${(workflow.total_cost_cents / 100).toFixed(2)}</p>
              <p className="text-xs text-muted-foreground">Total cost</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
              <Clock className="h-4 w-4 text-primary" />
            </div>
            <div>
              <p className="text-2xl font-bold">{formatDateTime(workflow.created_at)}</p>
              <p className="text-xs text-muted-foreground">Started</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Error banner */}
      {workflow.error_message && (
        <Card className="border-destructive/50 bg-destructive/5">
          <CardContent className="p-4 flex items-start gap-3">
            <XCircle className="h-5 w-5 text-destructive mt-0.5" />
            <div>
              <p className="font-medium text-destructive">Workflow Failed</p>
              <p className="text-sm text-muted-foreground mt-1">{workflow.error_message}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step-by-step progress */}
      <Card>
        <CardHeader>
          <CardTitle>Steps</CardTitle>
        </CardHeader>
        <CardContent>
          {steps.length === 0 ? (
            <p className="text-sm text-muted-foreground">No step data available yet.</p>
          ) : (
            <div className="space-y-0">
              {steps.map((step, idx) => {
                const config = stepStatusConfig[step.status] ?? stepStatusConfig.pending;
                const Icon = config.icon;
                const isLast = idx === steps.length - 1;

                return (
                  <div key={step.id} className="relative flex gap-4 pb-6">
                    {/* Vertical line */}
                    {!isLast && (
                      <div className="absolute left-[17px] top-[36px] bottom-0 w-px bg-border" />
                    )}

                    {/* Icon */}
                    <div className="relative z-10 flex h-9 w-9 shrink-0 items-center justify-center rounded-full border bg-card">
                      <Icon className={`h-4 w-4 ${config.color} ${step.status === "running" ? "animate-spin" : ""}`} />
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0 pt-1">
                      <div className="flex items-center justify-between gap-2">
                        <div>
                          <p className="text-sm font-medium">{step.step_name}</p>
                          <p className="text-xs text-muted-foreground">
                            {step.agent_name ? `Agent: ${step.agent_name}` : "System step"}
                            {step.started_at && ` · ${formatDateTime(step.started_at)}`}
                          </p>
                        </div>
                        <div className="flex items-center gap-3 text-xs text-muted-foreground shrink-0">
                          {step.tokens_used > 0 && (
                            <span>{step.tokens_used.toLocaleString()} tok</span>
                          )}
                          {step.cost_cents > 0 && (
                            <span>${(step.cost_cents / 100).toFixed(2)}</span>
                          )}
                          {step.duration_ms > 0 && (
                            <span>{step.duration_ms < 1000 ? `${step.duration_ms}ms` : `${(step.duration_ms / 1000).toFixed(1)}s`}</span>
                          )}
                          <Badge variant={step.status === "completed" ? "success" : step.status === "failed" ? "destructive" : step.status === "waiting_approval" ? "warning" : "secondary"}>
                            {config.label}
                          </Badge>
                        </div>
                      </div>

                      {/* Error message */}
                      {step.error_message && (
                        <p className="mt-1.5 text-xs text-destructive bg-destructive/10 rounded px-2 py-1">
                          {step.error_message}
                        </p>
                      )}

                      {/* Approval link */}
                      {step.status === "waiting_approval" && step.approval_id && (
                        <p className="mt-1.5 text-xs text-amber-600 bg-amber-50 rounded px-2 py-1">
                          Waiting for approval. Review it on the Approvals page.
                        </p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
