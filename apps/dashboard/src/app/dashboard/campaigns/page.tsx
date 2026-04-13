import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import { StatusDot } from "@/components/ui/status-dot";
import { campaigns } from "@/data/seed";
import { formatCurrency, formatDate } from "@/lib/utils";
import { Plus } from "lucide-react";
import type { Campaign } from "@/types";

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
};

const columns = [
  {
    header: "Campaign",
    cell: (row: Campaign) => (
      <div>
        <p className="font-medium">{row.name}</p>
        <p className="text-xs text-muted-foreground">{row.businessName}</p>
      </div>
    ),
  },
  {
    header: "Channel",
    cell: (row: Campaign) => (
      <Badge variant="secondary">{channelLabel[row.channel]}</Badge>
    ),
  },
  {
    header: "Status",
    cell: (row: Campaign) => (
      <Badge variant={statusVariant[row.status]}>
        <StatusDot status={row.status} className="mr-1.5" />
        {row.status}
      </Badge>
    ),
  },
  {
    header: "Budget",
    cell: (row: Campaign) => (
      <span className="font-medium">{formatCurrency(row.budget)}</span>
    ),
    className: "text-right",
  },
  {
    header: "Spent",
    cell: (row: Campaign) => {
      const pct = Math.round((row.spent / row.budget) * 100);
      return (
        <div className="text-right">
          <span className="text-muted-foreground">
            {formatCurrency(row.spent)}
          </span>
          <span className="ml-1 text-xs text-muted-foreground">({pct}%)</span>
        </div>
      );
    },
    className: "text-right",
  },
  {
    header: "Impressions",
    cell: (row: Campaign) => (
      <span className="text-muted-foreground">
        {(row.impressions / 1000).toFixed(0)}k
      </span>
    ),
    className: "text-right",
  },
  {
    header: "Conversions",
    cell: (row: Campaign) => (
      <span className="font-medium">{row.conversions.toLocaleString()}</span>
    ),
    className: "text-right",
  },
  {
    header: "Period",
    cell: (row: Campaign) => (
      <span className="text-xs text-muted-foreground">
        {formatDate(row.startDate)} — {formatDate(row.endDate)}
      </span>
    ),
  },
];

export default function CampaignsPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Campaigns"
        description="Ad campaigns and marketing initiatives."
      >
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          New Campaign
        </Button>
      </PageHeader>

      <Card>
        <CardContent className="p-0">
          <DataTable columns={columns} data={campaigns} />
        </CardContent>
      </Card>
    </div>
  );
}
