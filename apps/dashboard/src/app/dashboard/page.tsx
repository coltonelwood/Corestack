import { MetricCard } from "@/components/dashboard/metric-card";
import { ActivityFeed } from "@/components/dashboard/activity-feed";
import { RecentTasks } from "@/components/dashboard/recent-tasks";
import { PerformanceSummary } from "@/components/dashboard/performance-summary";
import { PageHeader } from "@/components/ui/page-header";
import { businesses, approvals, campaigns } from "@/data/seed";
import { formatCurrency } from "@/lib/utils";

export default function DashboardPage() {
  const totalRevenue = businesses.reduce((sum, b) => sum + b.revenue, 0);
  const totalSpend = businesses.reduce((sum, b) => sum + b.spend, 0);
  const estimatedProfit = totalRevenue - totalSpend;
  const activeBiz = businesses.filter((b) => b.status === "active").length;
  const activeCampaigns = campaigns.filter((c) => c.status === "active").length;
  const pendingApprovals = approvals.filter((a) => a.status === "pending").length;

  const metrics = [
    {
      title: "Total Revenue",
      value: formatCurrency(totalRevenue),
      change: "+12.5%",
      changeType: "positive" as const,
      icon: "revenue",
    },
    {
      title: "Total Spend",
      value: formatCurrency(totalSpend),
      change: "+4.2%",
      changeType: "negative" as const,
      icon: "spend",
    },
    {
      title: "Estimated Profit",
      value: formatCurrency(estimatedProfit),
      change: "+18.3%",
      changeType: "positive" as const,
      icon: "profit",
    },
    {
      title: "Active Businesses",
      value: String(activeBiz),
      change: "+1",
      changeType: "positive" as const,
      icon: "businesses",
    },
    {
      title: "Active Campaigns",
      value: String(activeCampaigns),
      change: "+2",
      changeType: "positive" as const,
      icon: "campaigns",
    },
    {
      title: "Pending Approvals",
      value: String(pendingApprovals),
      change: "3 new",
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

      {/* Metric cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {metrics.map((m) => (
          <MetricCard key={m.title} {...m} />
        ))}
      </div>

      {/* Main content grid */}
      <div className="grid gap-6 lg:grid-cols-5">
        <div className="lg:col-span-3 space-y-6">
          <RecentTasks />
          <PerformanceSummary />
        </div>
        <div className="lg:col-span-2">
          <ActivityFeed />
        </div>
      </div>
    </div>
  );
}
