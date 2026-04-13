import { MetricCard } from "@/components/dashboard/metric-card";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { StatusDot } from "@/components/ui/status-dot";
import { Avatar } from "@/components/ui/avatar";
import { EmptyState } from "@/components/state/empty";
import { formatCurrency, formatDateTime } from "@/lib/utils";
import { createDataClient } from "@/lib/supabase/data";

async function getDashboardData() {
  const supabase = createDataClient();

  const [bizRes, campRes, taskRes, runRes, apprRes] = await Promise.all([
    supabase.from("businesses").select("*"),
    supabase.from("campaigns").select("*"),
    supabase.from("tasks").select("*, businesses(name)").order("created_at", { ascending: false }).limit(5),
    supabase.from("agent_runs").select("*, businesses(name)").order("started_at", { ascending: false }).limit(7),
    supabase.from("approvals").select("*").eq("status", "pending"),
  ]);

  return {
    businesses: bizRes.data ?? [],
    campaigns: campRes.data ?? [],
    recentTasks: taskRes.data ?? [],
    recentRuns: runRes.data ?? [],
    pendingApprovals: apprRes.data ?? [],
  };
}

const priorityVariant: Record<string, "default" | "secondary" | "destructive" | "warning" | "success" | "outline"> = {
  low: "secondary",
  medium: "outline",
  high: "warning",
  critical: "destructive",
};

const agentInitials: Record<string, string> = {
  "Ads Manager": "AM",
  "Analytics Agent": "AA",
  "Content Writer": "CW",
  "Operations Agent": "OA",
  "Research Analyst": "RA",
  "Outreach Agent": "OT",
};

export default async function DashboardPage() {
  const { businesses, campaigns, recentTasks, recentRuns, pendingApprovals } =
    await getDashboardData();

  const activeBiz = businesses.filter((b) => b.status === "active");
  const activeCampaigns = campaigns.filter((c) => c.status === "active");

  // Aggregate finances from campaigns (budget = revenue proxy, spent = spend)
  const totalBudget = campaigns.reduce((s, c) => s + c.budget_cents, 0);
  const totalSpent = campaigns.reduce((s, c) => s + c.spent_cents, 0);
  const totalProfit = totalBudget - totalSpent;

  const metrics = [
    {
      title: "Total Budget",
      value: formatCurrency(totalBudget / 100),
      change: "+12.5%",
      changeType: "positive" as const,
      icon: "revenue",
    },
    {
      title: "Total Spend",
      value: formatCurrency(totalSpent / 100),
      change: "+4.2%",
      changeType: "negative" as const,
      icon: "spend",
    },
    {
      title: "Remaining",
      value: formatCurrency(totalProfit / 100),
      change: "+18.3%",
      changeType: "positive" as const,
      icon: "profit",
    },
    {
      title: "Active Businesses",
      value: String(activeBiz.length),
      change: `${businesses.length} total`,
      changeType: "neutral" as const,
      icon: "businesses",
    },
    {
      title: "Active Campaigns",
      value: String(activeCampaigns.length),
      change: `${campaigns.length} total`,
      changeType: "neutral" as const,
      icon: "campaigns",
    },
    {
      title: "Pending Approvals",
      value: String(pendingApprovals.length),
      change: pendingApprovals.length > 0 ? "needs review" : "all clear",
      changeType: "neutral" as const,
      icon: "approvals",
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dashboard"
        description="Overview of all autonomous business operations."
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {metrics.map((m) => (
          <MetricCard key={m.title} {...m} />
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        {/* Recent tasks */}
        <div className="lg:col-span-3 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Recent Tasks</CardTitle>
            </CardHeader>
            <CardContent>
              {recentTasks.length === 0 ? (
                <EmptyState title="No tasks yet" description="Tasks will appear here once agents start working." />
              ) : (
                <div className="space-y-3">
                  {recentTasks.map((task) => (
                    <div key={task.id} className="flex items-start justify-between gap-3 rounded-md border p-3">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <StatusDot status={task.status} />
                          <p className="text-sm font-medium truncate">{task.title}</p>
                        </div>
                        <div className="mt-1.5 flex items-center gap-2 text-xs text-muted-foreground">
                          <span>{task.assigned_agent ?? "Unassigned"}</span>
                          <span>&middot;</span>
                          <span>{(task.businesses as { name: string } | null)?.name ?? "—"}</span>
                        </div>
                      </div>
                      <div className="flex flex-col items-end gap-1.5 shrink-0">
                        <Badge variant={priorityVariant[task.priority]}>{task.priority}</Badge>
                        <span className="text-xs text-muted-foreground">{formatDateTime(task.created_at)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Performance summary */}
          <Card>
            <CardHeader>
              <CardTitle>Business Performance</CardTitle>
            </CardHeader>
            <CardContent>
              {activeBiz.length === 0 ? (
                <EmptyState title="No active businesses" description="Create a business to get started." />
              ) : (
                <div className="space-y-3">
                  {activeBiz.map((biz) => {
                    const bizCamps = campaigns.filter((c) => c.business_id === biz.id);
                    const bizBudget = bizCamps.reduce((s, c) => s + c.budget_cents, 0);
                    const bizSpent = bizCamps.reduce((s, c) => s + c.spent_cents, 0);
                    const utilization = bizBudget > 0 ? Math.round((bizSpent / bizBudget) * 100) : 0;

                    return (
                      <div key={biz.id} className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span className="font-medium">{biz.name}</span>
                          <span className="text-muted-foreground">{formatCurrency(bizBudget / 100)}</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="flex-1 h-2 rounded-full bg-secondary">
                            <div className="h-2 rounded-full bg-primary transition-all" style={{ width: `${Math.min(utilization, 100)}%` }} />
                          </div>
                          <span className="text-xs font-medium text-muted-foreground w-10 text-right">{utilization}%</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Activity feed */}
        <div className="lg:col-span-2">
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Agent Activity</CardTitle>
            </CardHeader>
            <CardContent>
              {recentRuns.length === 0 ? (
                <EmptyState title="No activity yet" description="Agent runs will appear here." />
              ) : (
                <div className="space-y-4">
                  {recentRuns.map((run) => (
                    <div key={run.id} className="flex items-start gap-3">
                      <Avatar fallback={agentInitials[run.agent_name] ?? run.agent_name.charAt(0)} size="sm" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm">
                          <span className="font-medium">{run.agent_name}</span>{" "}
                          <span className="text-muted-foreground">
                            {run.status === "completed" ? "completed" : run.status === "running" ? "is working on" : run.status === "failed" ? "failed" : "queued"}
                          </span>{" "}
                          <span className="font-medium">{(run.businesses as { name: string } | null)?.name ?? ""}</span>
                        </p>
                        <p className="text-xs text-muted-foreground mt-0.5">{formatDateTime(run.started_at)}</p>
                      </div>
                      <StatusDot status={run.status} />
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
