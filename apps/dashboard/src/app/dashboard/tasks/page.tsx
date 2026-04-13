import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { StatusDot } from "@/components/ui/status-dot";
import { EmptyState } from "@/components/state/empty";
import { formatDateTime } from "@/lib/utils";
import { getTasks } from "@/app/actions/tasks";
import { getBusinesses } from "@/app/actions/businesses";
import { TaskPageActions } from "./actions";

type TaskWithBiz = Awaited<ReturnType<typeof getTasks>>[number];

const statusVariant: Record<string, "success" | "warning" | "secondary" | "destructive"> = {
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
    cell: (row: TaskWithBiz) => (
      <div className="max-w-xs">
        <p className="font-medium truncate">{row.title}</p>
        <p className="text-xs text-muted-foreground truncate">{row.description ?? ""}</p>
      </div>
    ),
  },
  {
    header: "Status",
    cell: (row: TaskWithBiz) => (
      <Badge variant={statusVariant[row.status] ?? "secondary"}>
        <StatusDot status={row.status} className="mr-1.5" />
        {row.status.replace("_", " ")}
      </Badge>
    ),
  },
  {
    header: "Priority",
    cell: (row: TaskWithBiz) => (
      <Badge variant={priorityVariant[row.priority] ?? "outline"}>{row.priority}</Badge>
    ),
  },
  {
    header: "Agent",
    cell: (row: TaskWithBiz) => (
      <span className="text-muted-foreground">{row.assigned_agent ?? "Unassigned"}</span>
    ),
  },
  {
    header: "Business",
    cell: (row: TaskWithBiz) => (
      <span className="text-muted-foreground">
        {(row.businesses as { name: string } | null)?.name ?? "—"}
      </span>
    ),
  },
  {
    header: "Created",
    cell: (row: TaskWithBiz) => (
      <span className="text-muted-foreground">{formatDateTime(row.created_at)}</span>
    ),
  },
  {
    header: "Completed",
    cell: (row: TaskWithBiz) => (
      <span className="text-muted-foreground">
        {row.completed_at ? formatDateTime(row.completed_at) : "—"}
      </span>
    ),
  },
];

export default async function TasksPage() {
  const [tasks, businesses] = await Promise.all([
    getTasks(),
    getBusinesses(),
  ]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Tasks"
        description="All tasks assigned to AI agents."
      >
        <TaskPageActions businesses={businesses} />
      </PageHeader>

      {tasks.length === 0 ? (
        <Card>
          <CardContent className="p-0">
            <EmptyState
              title="No tasks yet"
              description="Create a task to assign work to an AI agent."
            />
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0">
            <DataTable columns={columns} data={tasks} />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
