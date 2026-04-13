import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { StatusDot } from "@/components/ui/status-dot";
import { EmptyState } from "@/components/state/empty";
import { formatDateTime } from "@/lib/utils";
import { getAgentRuns } from "@/app/actions/agent-runs";

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
      <span className="text-muted-foreground font-mono text-xs">
        {formatDuration(row.duration_ms)}
      </span>
    ),
    className: "text-right",
  },
  {
    header: "Tokens",
    cell: (row: RunWithJoins) => (
      <span className="text-muted-foreground font-mono text-xs">
        {row.tokens_used.toLocaleString()}
      </span>
    ),
    className: "text-right",
  },
  {
    header: "Cost",
    cell: (row: RunWithJoins) => (
      <span className="text-muted-foreground font-mono text-xs">
        ${(row.cost_cents / 100).toFixed(2)}
      </span>
    ),
    className: "text-right",
  },
  {
    header: "Started",
    cell: (row: RunWithJoins) => (
      <span className="text-muted-foreground">{formatDateTime(row.started_at)}</span>
    ),
  },
];

export default async function AgentRunsPage() {
  const runs = await getAgentRuns();

  return (
    <div className="space-y-6">
      <PageHeader
        title="Agent Runs"
        description="Execution history for all AI agents."
      />

      {runs.length === 0 ? (
        <Card>
          <CardContent className="p-0">
            <EmptyState
              title="No agent runs yet"
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
