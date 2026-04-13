import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { StatusDot } from "@/components/ui/status-dot";
import { agentRuns } from "@/data/seed";
import { formatDateTime } from "@/lib/utils";
import type { AgentRun } from "@/types";

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

function formatDuration(seconds: number | null): string {
  if (seconds === null) return "—";
  if (seconds < 60) return `${seconds}s`;
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}m ${secs}s`;
}

const columns = [
  {
    header: "Agent",
    cell: (row: AgentRun) => (
      <div>
        <p className="font-medium">{row.agentName}</p>
        <p className="text-xs text-muted-foreground">{row.businessName}</p>
      </div>
    ),
  },
  {
    header: "Type",
    cell: (row: AgentRun) => (
      <Badge variant="secondary">{typeLabel[row.agentType]}</Badge>
    ),
  },
  {
    header: "Task",
    cell: (row: AgentRun) => (
      <span className="text-sm max-w-xs truncate block">
        {row.taskDescription}
      </span>
    ),
  },
  {
    header: "Status",
    cell: (row: AgentRun) => (
      <Badge variant={statusVariant[row.status]}>
        <StatusDot status={row.status} className="mr-1.5" />
        {row.status}
      </Badge>
    ),
  },
  {
    header: "Duration",
    cell: (row: AgentRun) => (
      <span className="text-muted-foreground font-mono text-xs">
        {formatDuration(row.duration)}
      </span>
    ),
    className: "text-right",
  },
  {
    header: "Tokens",
    cell: (row: AgentRun) => (
      <span className="text-muted-foreground font-mono text-xs">
        {row.tokensUsed.toLocaleString()}
      </span>
    ),
    className: "text-right",
  },
  {
    header: "Started",
    cell: (row: AgentRun) => (
      <span className="text-muted-foreground">
        {formatDateTime(row.startedAt)}
      </span>
    ),
  },
];

export default function AgentRunsPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Agent Runs"
        description="Execution history for all AI agents."
      />

      <Card>
        <CardContent className="p-0">
          <DataTable columns={columns} data={agentRuns} />
        </CardContent>
      </Card>
    </div>
  );
}
