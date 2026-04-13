import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { StatusDot } from "@/components/ui/status-dot";
import { EmptyState } from "@/components/state/empty";
import { formatCurrency, formatDate } from "@/lib/utils";
import { getCampaigns } from "@/app/actions/campaigns";
import { getBusinesses } from "@/app/actions/businesses";
import { CampaignPageActions } from "./actions";
import { TrendingUp, TrendingDown, Pause, XCircle, Minus } from "lucide-react";

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

// Decision display config
const decisionConfig: Record<string, { icon: typeof TrendingUp; color: string; bg: string; label: string }> = {
  scale: { icon: TrendingUp, color: "text-emerald-600", bg: "bg-emerald-50 border-emerald-200", label: "Scale Up" },
  scale_up: { icon: TrendingUp, color: "text-emerald-600", bg: "bg-emerald-50 border-emerald-200", label: "Scale Up" },
  hold: { icon: Minus, color: "text-blue-600", bg: "bg-blue-50 border-blue-200", label: "Hold" },
  maintain: { icon: Minus, color: "text-blue-600", bg: "bg-blue-50 border-blue-200", label: "Maintain" },
  pause: { icon: Pause, color: "text-amber-600", bg: "bg-amber-50 border-amber-200", label: "Pause" },
  scale_down: { icon: TrendingDown, color: "text-amber-600", bg: "bg-amber-50 border-amber-200", label: "Scale Down" },
  kill: { icon: XCircle, color: "text-red-600", bg: "bg-red-50 border-red-200", label: "Kill" },
};

type MetadataWithOpt = { last_optimization?: { decision?: string; confidence?: number; reason?: string; recommended_action?: string; risk_level?: string; recommended_budget_change_pct?: number; overrides?: string[] } };

function CampaignRecommendations({ campaigns }: { campaigns: CampaignWithBiz[] }) {
  const withRecs = campaigns.filter((c) => {
    const meta = c.metadata as MetadataWithOpt | null;
    return meta?.last_optimization?.decision;
  });

  if (withRecs.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>AI Recommendations</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {withRecs.map((campaign) => {
            const meta = campaign.metadata as MetadataWithOpt;
            const opt = meta.last_optimization!;
            const config = decisionConfig[opt.decision ?? "hold"] ?? decisionConfig.hold;
            const Icon = config.icon;

            return (
              <div key={campaign.id} className={`rounded-lg border p-4 ${config.bg}`}>
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <div className={`mt-0.5 ${config.color}`}>
                      <Icon className="h-5 w-5" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-medium">{campaign.name}</p>
                        <Badge variant={opt.risk_level === "high" || opt.risk_level === "critical" ? "destructive" : "secondary"}>
                          {opt.risk_level}
                        </Badge>
                      </div>
                      <p className="text-sm mt-1">{opt.reason}</p>
                      {opt.recommended_action && (
                        <p className="text-sm font-medium mt-1.5">{opt.recommended_action}</p>
                      )}
                      {opt.overrides && opt.overrides.length > 0 && (
                        <div className="mt-2 space-y-1">
                          {opt.overrides.map((o, i) => (
                            <p key={i} className="text-xs text-muted-foreground">Guardrail: {o}</p>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="text-right shrink-0">
                    <p className={`text-lg font-bold ${config.color}`}>{config.label}</p>
                    <p className="text-xs text-muted-foreground">
                      {Math.round((opt.confidence ?? 0) * 100)}% confidence
                    </p>
                    {opt.recommended_budget_change_pct !== undefined && opt.recommended_budget_change_pct !== 0 && (
                      <p className="text-xs text-muted-foreground mt-0.5">
                        Budget: {opt.recommended_budget_change_pct > 0 ? "+" : ""}{opt.recommended_budget_change_pct}%
                      </p>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

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

      <CampaignRecommendations campaigns={campaigns} />

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
