import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { StatusDot } from "@/components/ui/status-dot";
import { EmptyState } from "@/components/state/empty";
import { formatCurrency, formatDateTime } from "@/lib/utils";
import { getApprovals } from "@/app/actions/approvals";
import { ApprovalActions } from "./actions";

type ApprovalWithBiz = Awaited<ReturnType<typeof getApprovals>>[number];

const statusVariant: Record<string, "warning" | "success" | "destructive"> = {
  pending: "warning",
  approved: "success",
  rejected: "destructive",
};

const typeLabel: Record<string, string> = {
  campaign_launch: "Campaign Launch",
  budget_increase: "Budget Increase",
  content_publish: "Content Publish",
  product_listing: "Product Listing",
  price_change: "Price Change",
  other: "Other",
};

const columns = [
  {
    header: "Request",
    cell: (row: ApprovalWithBiz) => (
      <div className="max-w-xs">
        <p className="font-medium">{row.title}</p>
        <p className="text-xs text-muted-foreground truncate">{row.description ?? ""}</p>
      </div>
    ),
  },
  {
    header: "Type",
    cell: (row: ApprovalWithBiz) => (
      <Badge variant="secondary">{typeLabel[row.type] ?? row.type}</Badge>
    ),
  },
  {
    header: "Status",
    cell: (row: ApprovalWithBiz) => (
      <Badge variant={statusVariant[row.status] ?? "warning"}>
        <StatusDot status={row.status} className="mr-1.5" />
        {row.status}
      </Badge>
    ),
  },
  {
    header: "Requested By",
    cell: (row: ApprovalWithBiz) => (
      <span className="text-muted-foreground">{row.requested_by}</span>
    ),
  },
  {
    header: "Business",
    cell: (row: ApprovalWithBiz) => (
      <span className="text-muted-foreground">
        {(row.businesses as { name: string } | null)?.name ?? "—"}
      </span>
    ),
  },
  {
    header: "Amount",
    cell: (row: ApprovalWithBiz) => (
      <span className="font-medium">
        {row.amount_cents ? formatCurrency(row.amount_cents / 100) : "—"}
      </span>
    ),
    className: "text-right",
  },
  {
    header: "Submitted",
    cell: (row: ApprovalWithBiz) => (
      <span className="text-muted-foreground">{formatDateTime(row.created_at)}</span>
    ),
  },
  {
    header: "Actions",
    cell: (row: ApprovalWithBiz) =>
      row.status === "pending" ? (
        <ApprovalActions id={row.id} />
      ) : (
        <span className="text-xs text-muted-foreground">
          {row.reviewed_at ? formatDateTime(row.reviewed_at) : ""}
        </span>
      ),
  },
];

export default async function ApprovalsPage() {
  const approvals = await getApprovals();
  const pendingCount = approvals.filter((a) => a.status === "pending").length;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Approvals"
        description={
          pendingCount > 0
            ? `${pendingCount} pending approval${pendingCount !== 1 ? "s" : ""} requiring your review.`
            : "All approvals have been reviewed."
        }
      />

      {approvals.length === 0 ? (
        <Card>
          <CardContent className="p-0">
            <EmptyState
              title="No approvals yet"
              description="Approval requests from agents will appear here."
            />
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0">
            <DataTable columns={columns} data={approvals} />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
