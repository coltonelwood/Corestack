import { Suspense } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { StatusDot } from "@/components/ui/status-dot";
import { EmptyState } from "@/components/state/empty";
import { StatusFilter } from "@/components/ui/status-filter";
import { formatCurrency, formatDateTime } from "@/lib/utils";
import { getApprovals } from "@/app/actions/approvals";
import { getUserWithRole } from "@/app/actions/auth";
import { hasPermission } from "@/lib/rbac";
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

const baseColumns = [
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
    header: "From",
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
      <span className="font-medium tabular-nums">
        {row.amount_cents ? formatCurrency(row.amount_cents / 100) : "—"}
      </span>
    ),
    className: "text-right",
  },
  {
    header: "Submitted",
    cell: (row: ApprovalWithBiz) => (
      <span className="text-muted-foreground tabular-nums">{formatDateTime(row.created_at)}</span>
    ),
  },
];

function getActionColumn(canDecide: boolean) {
  return {
    header: "",
    cell: (row: ApprovalWithBiz) => {
      if (row.status === "pending" && canDecide) {
        return <ApprovalActions id={row.id} />;
      }
      if (row.status === "pending") {
        return <span className="text-xs text-muted-foreground">Pending</span>;
      }
      return (
        <span className="text-xs text-muted-foreground tabular-nums">
          {row.reviewed_at ? formatDateTime(row.reviewed_at) : ""}
        </span>
      );
    },
  };
}

interface Props {
  searchParams: Promise<{ status?: string }>;
}

export default async function ApprovalsPage({ searchParams }: Props) {
  const params = await searchParams;
  const [allApprovals, user] = await Promise.all([getApprovals(), getUserWithRole()]);
  const canDecide = user ? hasPermission(user.role, "approvals:decide") : false;
  const allColumns = [...baseColumns, getActionColumn(canDecide)];

  const approvals = params.status
    ? allApprovals.filter((a) => a.status === params.status)
    : allApprovals;

  const counts = {
    all: allApprovals.length,
    pending: allApprovals.filter((a) => a.status === "pending").length,
    approved: allApprovals.filter((a) => a.status === "approved").length,
    rejected: allApprovals.filter((a) => a.status === "rejected").length,
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Approvals"
        description={
          counts.pending > 0
            ? `${counts.pending} pending approval${counts.pending !== 1 ? "s" : ""} requiring your review.`
            : "All approvals have been reviewed."
        }
        badge={counts.pending > 0 ? <Badge variant="warning">{counts.pending} pending</Badge> : undefined}
      />

      <Suspense>
        <StatusFilter
          options={[
            { label: "All", value: "", count: counts.all },
            { label: "Pending", value: "pending", count: counts.pending },
            { label: "Approved", value: "approved", count: counts.approved },
            { label: "Rejected", value: "rejected", count: counts.rejected },
          ]}
        />
      </Suspense>

      {approvals.length === 0 ? (
        <Card>
          <CardContent className="p-0">
            <EmptyState
              title={params.status ? `No ${params.status} approvals` : "No approvals yet"}
              description="Approval requests from agents will appear here."
            />
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0">
            <DataTable columns={allColumns} data={approvals} />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
