import { Suspense } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { StatusDot } from "@/components/ui/status-dot";
import { EmptyState } from "@/components/state/empty";
import { StatusFilter } from "@/components/ui/status-filter";
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
      <span className="text-muted-foreground tabular-nums">{formatDateTime(row.created_at)}</span>
    ),
  },
];

interface Props {
  searchParams: Promise<{ status?: string }>;
}

export default async function TasksPage({ searchParams }: Props) {
  const params = await searchParams;
  const [allTasks, businesses] = await Promise.all([getTasks(), getBusinesses()]);

  const tasks = params.status
    ? allTasks.filter((t) => t.status === params.status)
    : allTasks;

  const counts = {
    all: allTasks.length,
    pending: allTasks.filter((t) => t.status === "pending").length,
    in_progress: allTasks.filter((t) => t.status === "in_progress").length,
    completed: allTasks.filter((t) => t.status === "completed").length,
    failed: allTasks.filter((t) => t.status === "failed").length,
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Tasks"
        description="All tasks assigned to AI agents."
        badge={<Badge variant="secondary">{counts.all}</Badge>}
      >
        <TaskPageActions businesses={businesses} />
      </PageHeader>

      <Suspense>
        <StatusFilter
          options={[
            { label: "All", value: "", count: counts.all },
            { label: "Pending", value: "pending", count: counts.pending },
            { label: "In Progress", value: "in_progress", count: counts.in_progress },
            { label: "Completed", value: "completed", count: counts.completed },
            { label: "Failed", value: "failed", count: counts.failed },
          ]}
        />
      </Suspense>

      {tasks.length === 0 ? (
        <Card>
          <CardContent className="p-0">
            <EmptyState
              title={params.status ? `No ${params.status.replace("_", " ")} tasks` : "No tasks yet"}
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
