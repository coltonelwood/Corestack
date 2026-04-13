import { MetricCard } from "@/components/dashboard/metric-card";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { StatusDot } from "@/components/ui/status-dot";
import { Avatar } from "@/components/ui/avatar";
import { EmptyState } from "@/components/state/empty";
import { formatCurrency, formatDateTime } from "@/lib/utils";
import { createDataClient } from "@/lib/supabase/data";
import Link from "next/link";
import { AlertTriangle, ArrowRight, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";

async function getDashboardData() {
  const supabase = createDataClient();

  const [bizRes, campRes, taskRes, runRes, apprRes, wfRes] = await Promise.all([
    supabase.from("businesses").select("*"),
    supabase.from("campaigns").select("*"),
    supabase.from("tasks").select("*, businesses(name)").order("created_at", { ascending: false }).limit(5),
    supabase.from("agent_runs").select("*, businesses(name)").order("started_at", { ascending: false }).limit(7),
    supabase.from("approvals").select("*").eq("status", "pending"),
    supabase.from("workflow_runs").select("*").order("created_at", { ascending: false }).limit(3),
  ]);

  return {
    businesses: bizRes.data ?? [],
    campaigns: campRes.data ?? [],
    recentTasks: taskRes.data ?? [],
    recentRuns: runRes.data ?? [],
    pendingApprovals: apprRes.data ?? [],
    recentWorkflows: wfRes.data ?? [],
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
  const { businesses, campaigns, recentTasks, recentRuns, pendingApprovals, recentWorkflows } =
    await getDashboardData();

  const activeBiz = businesses.filter((b) => b.status === "active");
  const activeCampaigns = campaigns.filter((c) => c.status === "active");
  const totalBudget = campaigns.reduce((s, c) => s + c.budget_cents, 0);
  const totalSpent = campaigns.reduce((s, c) => s + c.spent_cents, 0);
  const totalRemaining = totalBudget - totalSpent;

  const metrics = [
    { title: "Total Budget", value: formatCurrency(totalBudget / 100), change: "+12.5%", changeType: "positive" as const, icon: "revenue" },
    { title: "Total Spend", value: formatCurrency(totalSpent / 100), change: "+4.2%", changeType: "negative" as const, icon: "spend" },
    { title: "Remaining", value: formatCurrency(totalRemaining / 100), change: "+18.3%", changeType: "positive" as const, icon: "profit" },
    { title: "Active Businesses", value: String(activeBiz.length), change: `${businesses.length} total`, changeType: "neutral" as const, icon: "businesses" },
    { title: "Active Campaigns", value: String(activeCampaigns.length), change: `${campaigns.length} total`, changeType: "neutral" as const, icon: "campaigns" },
    { title: "Pending Approvals", value: String(pendingApprovals.length), change: pendingApprovals.length > 0 ? "needs review" : "all clear", changeType: "neutral" as const, icon: "approvals" },
  ];

  return (
    <div className="space-y-6">
      <PageHeader title="Dashboard" description="Overview of all autonomous business operations." />

      {/* Approval urgency banner */}
      {pendingApprovals.length > 0 && (
        <Link href="/dashboard/approvals">
          <div className="flex items-center justify-between rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm transition-colors hover:bg-amber-100/80">
            <div className="flex items-center gap-3">
              <AlertTriangle className="h-4 w-4 text-amber-600" />
              <span className="font-medium text-amber-900">
                {pendingApprovals.length} approval{pendingApprovals.length !== 1 ? "s" : ""} waiting for your review
              </span>
            </div>
            <ArrowRight className="h-4 w-4 text-amber-600" />
          </div>
        </Link>
      )}

      {/* Metrics */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        {metrics.map((m) => (
          <MetricCard key={m.title} {...m} />
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        {/* Left column */}
        <div className="lg:col-span-5 space-y-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <CardTitle>Recent Tasks</CardTitle>
              <Link href="/dashboard/tasks">
                <Button variant="ghost" size="sm" className="text-xs text-muted-foreground h-7">View all</Button>
              </Link>
            </CardHeader>
            <CardContent>
              {recentTasks.length === 0 ? (
                <EmptyState title="No tasks yet" description="Tasks appear once agents start working." />
              ) : (
                <div className="space-y-2">
                  {recentTasks.map((task) => (
                    <div key={task.id} className="flex items-center justify-between gap-3 rounded-lg border px-3 py-2.5">
                      <div className="flex items-center gap-2.5 min-w-0">
                        <StatusDot status={task.status} />
                        <div className="min-w-0">
                          <p className="text-sm font-medium truncate">{task.title}</p>
                          <p className="text-xs text-muted-foreground">{task.assigned_agent ?? "Unassigned"}</p>
                        </div>
                      </div>
                      <Badge variant={priorityVariant[task.priority]} className="shrink-0">{task.priority}</Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <CardTitle>Budget Utilization</CardTitle>
              <Link href="/dashboard/businesses">
                <Button variant="ghost" size="sm" className="text-xs text-muted-foreground h-7">View all</Button>
              </Link>
            </CardHeader>
            <CardContent>
              {activeBiz.length === 0 ? (
                <EmptyState title="No active businesses" description="Create a business to get started." />
              ) : (
                <div className="space-y-4">
                  {activeBiz.map((biz) => {
                    const bizCamps = campaigns.filter((c) => c.business_id === biz.id);
                    const bizBudget = bizCamps.reduce((s, c) => s + c.budget_cents, 0);
                    const bizSpent = bizCamps.reduce((s, c) => s + c.spent_cents, 0);
                    const utilization = bizBudget > 0 ? Math.round((bizSpent / bizBudget) * 100) : 0;

                    return (
                      <div key={biz.id} className="space-y-1.5">
                        <div className="flex items-center justify-between text-sm">
                          <span className="font-medium">{biz.name}</span>
                          <span className="text-xs tabular-nums text-muted-foreground">{formatCurrency(bizSpent / 100)} / {formatCurrency(bizBudget / 100)}</span>
                        </div>
                        <div className="flex items-center gap-2.5">
                          <div className="flex-1 h-1.5 rounded-full bg-secondary overflow-hidden">
                            <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${Math.min(utilization, 100)}%` }} />
                          </div>
                          <span className="text-xs font-medium tabular-nums text-muted-foreground w-8 text-right">{utilization}%</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Middle column */}
        <div className="lg:col-span-4">
          <Card className="h-full">
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <CardTitle>Agent Activity</CardTitle>
              <Link href="/dashboard/agent-runs">
                <Button variant="ghost" size="sm" className="text-xs text-muted-foreground h-7">View all</Button>
              </Link>
            </CardHeader>
            <CardContent>
              {recentRuns.length === 0 ? (
                <EmptyState title="No activity yet" description="Agent runs will appear here." />
              ) : (
                <div className="space-y-3">
                  {recentRuns.map((run) => (
                    <div key={run.id} className="flex items-start gap-2.5">
                      <Avatar fallback={agentInitials[run.agent_name] ?? run.agent_name.charAt(0)} size="sm" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm leading-snug">
                          <span className="font-medium">{run.agent_name}</span>{" "}
                          <span className="text-muted-foreground">
                            {run.status === "completed" ? "completed" : run.status === "running" ? "is running" : run.status === "failed" ? "failed" : "queued"}
                          </span>
                        </p>
                        <p className="text-xs text-muted-foreground">{formatDateTime(run.started_at)}</p>
                      </div>
                      <StatusDot status={run.status} className="mt-1.5" />
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right column */}
        <div className="lg:col-span-3">
          <Card className="h-full">
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <CardTitle>Workflows</CardTitle>
              <Link href="/dashboard/workflows">
                <Button variant="ghost" size="sm" className="text-xs text-muted-foreground h-7">View all</Button>
              </Link>
            </CardHeader>
            <CardContent>
              {recentWorkflows.length === 0 ? (
                <EmptyState title="No workflows" description="Launch a product to start." />
              ) : (
                <div className="space-y-3">
                  {recentWorkflows.map((wf) => (
                    <Link key={wf.id} href={`/dashboard/workflows/${wf.id}`}>
                      <div className="rounded-lg border p-3 hover:bg-muted/30 transition-colors">
                        <div className="flex items-center gap-2">
                          <Zap className="h-3.5 w-3.5 text-primary" />
                          <p className="text-sm font-medium truncate">{wf.name}</p>
                        </div>
                        <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
                          <span>{wf.completed_steps}/{wf.total_steps} steps</span>
                          <Badge variant={wf.status === "completed" ? "success" : wf.status === "failed" ? "destructive" : wf.status === "paused" ? "warning" : "secondary"}>
                            {wf.status === "paused" ? "awaiting" : wf.status}
                          </Badge>
                        </div>
                        <div className="mt-2 h-1 rounded-full bg-secondary overflow-hidden">
                          <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${wf.total_steps > 0 ? (wf.completed_steps / wf.total_steps) * 100 : 0}%` }} />
                        </div>
                      </div>
                    </Link>
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
