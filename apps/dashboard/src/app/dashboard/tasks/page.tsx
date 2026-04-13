import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { StatusDot } from "@/components/ui/status-dot";
import { tasks } from "@/data/seed";
import { formatDateTime } from "@/lib/utils";
import type { Task } from "@/types";

const statusVariant: Record<string, "success" | "warning" | "secondary" | "destructive" | "default"> = {
  pending: "secondary",
  in_progress: "warning",
  completed: "success",
  failed: "destructive",
};

const priorityVariant: Record<string, "secondary" | "outline" | "warning" | "destructive"> = {
  low: "secondary",
  medium: "outline",
  high: "warning",
  critical: "destructive",
};

const columns = [
  {
    header: "Task",
    cell: (row: Task) => (
      <div className="max-w-xs">
        <p className="font-medium truncate">{row.title}</p>
        <p className="text-xs text-muted-foreground truncate">
          {row.description}
        </p>
      </div>
    ),
  },
  {
    header: "Status",
    cell: (row: Task) => (
      <Badge variant={statusVariant[row.status]}>
        <StatusDot status={row.status} className="mr-1.5" />
        {row.status.replace("_", " ")}
      </Badge>
    ),
  },
  {
    header: "Priority",
    cell: (row: Task) => (
      <Badge variant={priorityVariant[row.priority]}>{row.priority}</Badge>
    ),
  },
  {
    header: "Agent",
    cell: (row: Task) => (
      <span className="text-muted-foreground">{row.assignedAgent}</span>
    ),
  },
  {
    header: "Business",
    cell: (row: Task) => (
      <span className="text-muted-foreground">{row.businessName}</span>
    ),
  },
  {
    header: "Created",
    cell: (row: Task) => (
      <span className="text-muted-foreground">
        {formatDateTime(row.createdAt)}
      </span>
    ),
  },
  {
    header: "Completed",
    cell: (row: Task) => (
      <span className="text-muted-foreground">
        {row.completedAt ? formatDateTime(row.completedAt) : "—"}
      </span>
    ),
  },
];

export default function TasksPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Tasks"
        description="All tasks assigned to AI agents."
      />

      <Card>
        <CardContent className="p-0">
          <DataTable columns={columns} data={tasks} />
        </CardContent>
      </Card>
    </div>
  );
}
