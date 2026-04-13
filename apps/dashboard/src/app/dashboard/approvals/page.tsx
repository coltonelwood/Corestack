import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import { StatusDot } from "@/components/ui/status-dot";
import { approvals } from "@/data/seed";
import { formatCurrency, formatDateTime } from "@/lib/utils";
import { CheckCircle2, XCircle } from "lucide-react";
import type { Approval } from "@/types";

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
};

const columns = [
  {
    header: "Request",
    cell: (row: Approval) => (
      <div className="max-w-xs">
        <p className="font-medium">{row.title}</p>
        <p className="text-xs text-muted-foreground truncate">
          {row.description}
        </p>
      </div>
    ),
  },
  {
    header: "Type",
    cell: (row: Approval) => (
      <Badge variant="secondary">{typeLabel[row.type]}</Badge>
    ),
  },
  {
    header: "Status",
    cell: (row: Approval) => (
      <Badge variant={statusVariant[row.status]}>
        <StatusDot status={row.status} className="mr-1.5" />
        {row.status}
      </Badge>
    ),
  },
  {
    header: "Requested By",
    cell: (row: Approval) => (
      <span className="text-muted-foreground">{row.requestedBy}</span>
    ),
  },
  {
    header: "Business",
    cell: (row: Approval) => (
      <span className="text-muted-foreground">{row.businessName}</span>
    ),
  },
  {
    header: "Amount",
    cell: (row: Approval) => (
      <span className="font-medium">
        {row.amount ? formatCurrency(row.amount) : "—"}
      </span>
    ),
    className: "text-right",
  },
  {
    header: "Submitted",
    cell: (row: Approval) => (
      <span className="text-muted-foreground">
        {formatDateTime(row.createdAt)}
      </span>
    ),
  },
  {
    header: "Actions",
    cell: (row: Approval) =>
      row.status === "pending" ? (
        <div className="flex items-center gap-1">
          <Button size="sm" variant="ghost" className="h-8 w-8 p-0 text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50">
            <CheckCircle2 className="h-4 w-4" />
          </Button>
          <Button size="sm" variant="ghost" className="h-8 w-8 p-0 text-red-500 hover:text-red-600 hover:bg-red-50">
            <XCircle className="h-4 w-4" />
          </Button>
        </div>
      ) : (
        <span className="text-xs text-muted-foreground">
          {row.reviewedAt ? formatDateTime(row.reviewedAt) : ""}
        </span>
      ),
  },
];

export default function ApprovalsPage() {
  const pendingCount = approvals.filter((a) => a.status === "pending").length;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Approvals"
        description={`${pendingCount} pending approval${pendingCount !== 1 ? "s" : ""} requiring your review.`}
      />

      <Card>
        <CardContent className="p-0">
          <DataTable columns={columns} data={approvals} />
        </CardContent>
      </Card>
    </div>
  );
}
