import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { StatusDot } from "@/components/ui/status-dot";
import { EmptyState } from "@/components/state/empty";
import { formatCurrency, formatDate } from "@/lib/utils";
import { getCampaigns } from "@/app/actions/campaigns";
import { getBusinesses } from "@/app/actions/businesses";
import { CampaignPageActions } from "./actions";

type CampaignWithBiz = Awaited<ReturnType<typeof getCampaigns>>[number];

const statusVariant: Record<string, "success" | "warning" | "secondary" | "outline"> = {
  active: "success",
  paused: "warning",
  draft: "secondary",
  completed: "outline",
};

const channelLabel: Record<string, string> = {
  google: "Google Ads",
  meta: "Meta",
  tiktok: "TikTok",
  email: "Email",
  linkedin: "LinkedIn",
  other: "Other",
};

const columns = [
  {
    header: "Campaign",
    cell: (row: CampaignWithBiz) => (
      <div>
        <p className="font-medium">{row.name}</p>
        <p className="text-xs text-muted-foreground">
          {(row.businesses as { name: string } | null)?.name ?? "—"}
        </p>
      </div>
    ),
  },
  {
    header: "Channel",
    cell: (row: CampaignWithBiz) => (
      <Badge variant="secondary">{channelLabel[row.channel] ?? row.channel}</Badge>
    ),
  },
  {
    header: "Status",
    cell: (row: CampaignWithBiz) => (
      <Badge variant={statusVariant[row.status] ?? "secondary"}>
        <StatusDot status={row.status} className="mr-1.5" />
        {row.status}
      </Badge>
    ),
  },
  {
    header: "Budget",
    cell: (row: CampaignWithBiz) => (
      <span className="font-medium">{formatCurrency(row.budget_cents / 100)}</span>
    ),
    className: "text-right",
  },
  {
    header: "Spent",
    cell: (row: CampaignWithBiz) => {
      const pct = row.budget_cents > 0 ? Math.round((row.spent_cents / row.budget_cents) * 100) : 0;
      return (
        <div className="text-right">
          <span className="text-muted-foreground">{formatCurrency(row.spent_cents / 100)}</span>
          <span className="ml-1 text-xs text-muted-foreground">({pct}%)</span>
        </div>
      );
    },
    className: "text-right",
  },
  {
    header: "Conversions",
    cell: (row: CampaignWithBiz) => (
      <span className="font-medium">{row.conversions.toLocaleString()}</span>
    ),
    className: "text-right",
  },
  {
    header: "Period",
    cell: (row: CampaignWithBiz) => (
      <span className="text-xs text-muted-foreground">
        {row.start_date ? formatDate(row.start_date) : "—"} — {row.end_date ? formatDate(row.end_date) : "—"}
      </span>
    ),
  },
];

export default async function CampaignsPage() {
  const [campaigns, businesses] = await Promise.all([
    getCampaigns(),
    getBusinesses(),
  ]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Campaigns"
        description="Ad campaigns and marketing initiatives."
      >
        <CampaignPageActions businesses={businesses} />
      </PageHeader>

      {campaigns.length === 0 ? (
        <Card>
          <CardContent className="p-0">
            <EmptyState
              title="No campaigns yet"
              description="Create a campaign draft to get started."
            />
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0">
            <DataTable columns={columns} data={campaigns} />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
