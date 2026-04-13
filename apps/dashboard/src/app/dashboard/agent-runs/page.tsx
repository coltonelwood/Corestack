import { Suspense } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { StatusDot } from "@/components/ui/status-dot";
import { EmptyState } from "@/components/state/empty";
import { StatusFilter } from "@/components/ui/status-filter";
import { formatDateTime } from "@/lib/utils";
import { getAgentRuns } from "@/app/actions/agent-runs";
import { Activity, CheckCircle2, XCircle, Clock, Loader2 } from "lucide-react";

type RunWithJoins = Awaited<ReturnType<typeof getAgentRuns>>[number];

const statusVariant: Record<string, "success" | "warning" | "secondary" | "destructive"> = {
  running: "success",
  completed: "secondary",
  queued: "warning",
  failed: "destructive",
};

const typeLabel: Record<string, string> = {
  research: "Research",
  content: "Content",
  ads: "Ads",
  analytics: "Analytics",
  outreach: "Outreach",
  operations: "Operations",
};

function formatDuration(ms: number | null): string {
  if (ms === null) return "—";
  if (ms < 1000) return `${ms}ms`;
  const secs = Math.round(ms / 1000);
  if (secs < 60) return `${secs}s`;
  const mins = Math.floor(secs / 60);
  const rem = secs % 60;
  return `${mins}m ${rem}s`;
}

const columns = [
  {
    header: "Agent",
    cell: (row: RunWithJoins) => (
      <div>
        <p className="font-medium">{row.agent_name}</p>
        <p className="text-xs text-muted-foreground">
          {(row.businesses as { name: string } | null)?.name ?? "—"}
        </p>
      </div>
    ),
  },
  {
    header: "Type",
    cell: (row: RunWithJoins) => (
      <Badge variant="secondary">{typeLabel[row.agent_type] ?? row.agent_type}</Badge>
    ),
  },
  {
    header: "Task",
    cell: (row: RunWithJoins) => (
      <span className="text-sm max-w-xs truncate block">
        {(row.tasks as { title: string } | null)?.title ?? "—"}
      </span>
    ),
  },
  {
    header: "Status",
    cell: (row: RunWithJoins) => (
      <Badge variant={statusVariant[row.status] ?? "secondary"}>
        <StatusDot status={row.status} className="mr-1.5" />
        {row.status}
      </Badge>
    ),
  },
  {
    header: "Duration",
    cell: (row: RunWithJoins) => (
      <span className="text-muted-foreground font-mono text-xs tabular-nums">
        {formatDuration(row.duration_ms)}
      </span>
    ),
    className: "text-right",
  },
  {
    header: "Tokens",
    cell: (row: RunWithJoins) => (
      <span className="text-muted-foreground font-mono text-xs tabular-nums">
        {row.tokens_used.toLocaleString()}
      </span>
    ),
    className: "text-right",
  },
  {
    header: "Cost",
    cell: (row: RunWithJoins) => (
      <span className="text-muted-foreground font-mono text-xs tabular-nums">
        ${(row.cost_cents / 100).toFixed(2)}
      </span>
    ),
    className: "text-right",
  },
  {
    header: "Started",
    cell: (row: RunWithJoins) => (
      <span className="text-muted-foreground tabular-nums">{formatDateTime(row.started_at)}</span>
    ),
  },
];

interface Props {
  searchParams: Promise<{ status?: string }>;
}

export default async function AgentRunsPage({ searchParams }: Props) {
  const params = await searchParams;
  const allRuns = await getAgentRuns();

  const runs = params.status
    ? allRuns.filter((r) => r.status === params.status)
    : allRuns;

  const counts = {
    all: allRuns.length,
    running: allRuns.filter((r) => r.status === "running").length,
    completed: allRuns.filter((r) => r.status === "completed").length,
    failed: allRuns.filter((r) => r.status === "failed").length,
    queued: allRuns.filter((r) => r.status === "queued").length,
  };

  const totalTokens = allRuns.reduce((s, r) => s + r.tokens_used, 0);
  const totalCost = allRuns.reduce((s, r) => s + r.cost_cents, 0);
  const successRate = counts.all > 0
    ? Math.round((counts.completed / Math.max(counts.completed + counts.failed, 1)) * 100)
    : 0;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Agent Runs"
        description="Execution history for all AI agents."
        badge={<Badge variant="secondary">{counts.all} runs</Badge>}
      />

      {/* Health summary */}
      {counts.all > 0 && (
        <div className="grid gap-4 sm:grid-cols-4">
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <Activity className="h-4 w-4 text-primary" />
              <div>
                <p className="text-lg font-bold">{counts.running}</p>
                <p className="text-xs text-muted-foreground">Running now</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
              <div>
                <p className="text-lg font-bold">{successRate}%</p>
                <p className="text-xs text-muted-foreground">Success rate</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-lg font-bold tabular-nums">{totalTokens.toLocaleString()}</p>
                <p className="text-xs text-muted-foreground">Total tokens</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="h-4 w-4 text-muted-foreground text-xs font-bold">$</div>
              <div>
                <p className="text-lg font-bold tabular-nums">${(totalCost / 100).toFixed(2)}</p>
                <p className="text-xs text-muted-foreground">Total cost</p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <Suspense>
        <StatusFilter
          options={[
            { label: "All", value: "", count: counts.all },
            { label: "Running", value: "running", count: counts.running },
            { label: "Completed", value: "completed", count: counts.completed },
            { label: "Failed", value: "failed", count: counts.failed },
            { label: "Queued", value: "queued", count: counts.queued },
          ]}
        />
      </Suspense>

      {runs.length === 0 ? (
        <Card>
          <CardContent className="p-0">
            <EmptyState
              title={params.status ? `No ${params.status} runs` : "No agent runs yet"}
              description="Runs will appear here once agents start executing tasks."
            />
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0">
            <DataTable columns={columns} data={runs} />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
