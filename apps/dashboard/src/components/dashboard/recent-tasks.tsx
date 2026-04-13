import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { StatusDot } from "@/components/ui/status-dot";
import { tasks } from "@/data/seed";
import { formatDateTime } from "@/lib/utils";

const priorityVariant: Record<string, "default" | "secondary" | "destructive" | "warning" | "success" | "outline"> = {
  low: "secondary",
  medium: "outline",
  high: "warning",
  critical: "destructive",
};

export function RecentTasks() {
  const sortedTasks = [...tasks]
    .sort(
      (a, b) =>
        new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    )
    .slice(0, 5);

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Recent Tasks</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {sortedTasks.map((task) => (
            <div
              key={task.id}
              className="flex items-start justify-between gap-3 rounded-md border p-3"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <StatusDot status={task.status} />
                  <p className="text-sm font-medium truncate">{task.title}</p>
                </div>
                <div className="mt-1.5 flex items-center gap-2 text-xs text-muted-foreground">
                  <span>{task.assignedAgent}</span>
                  <span>&middot;</span>
                  <span>{task.businessName}</span>
                </div>
              </div>
              <div className="flex flex-col items-end gap-1.5 shrink-0">
                <Badge variant={priorityVariant[task.priority]}>
                  {task.priority}
                </Badge>
                <span className="text-xs text-muted-foreground">
                  {formatDateTime(task.createdAt)}
                </span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
