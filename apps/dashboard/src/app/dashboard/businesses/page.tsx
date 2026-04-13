import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import { StatusDot } from "@/components/ui/status-dot";
import { businesses } from "@/data/seed";
import { formatCurrency, formatDate } from "@/lib/utils";
import { Plus } from "lucide-react";
import type { Business } from "@/types";

const statusVariant: Record<string, "success" | "warning" | "secondary"> = {
  active: "success",
  paused: "warning",
  setup: "secondary",
};

const columns = [
  {
    header: "Business",
    cell: (row: Business) => (
      <div>
        <p className="font-medium">{row.name}</p>
        <p className="text-xs text-muted-foreground">{row.domain}</p>
      </div>
    ),
  },
  {
    header: "Status",
    cell: (row: Business) => (
      <Badge variant={statusVariant[row.status]}>
        <StatusDot status={row.status} className="mr-1.5" />
        {row.status}
      </Badge>
    ),
  },
  {
    header: "Revenue",
    cell: (row: Business) => (
      <span className="font-medium">{formatCurrency(row.revenue)}</span>
    ),
    className: "text-right",
  },
  {
    header: "Spend",
    cell: (row: Business) => (
      <span className="text-muted-foreground">{formatCurrency(row.spend)}</span>
    ),
    className: "text-right",
  },
  {
    header: "Profit",
    cell: (row: Business) => {
      const profit = row.revenue - row.spend;
      return (
        <span className={profit >= 0 ? "text-emerald-600 font-medium" : "text-red-500 font-medium"}>
          {formatCurrency(profit)}
        </span>
      );
    },
    className: "text-right",
  },
  {
    header: "Products",
    accessorKey: "productsCount" as const,
    className: "text-center",
  },
  {
    header: "Campaigns",
    accessorKey: "campaignsCount" as const,
    className: "text-center",
  },
  {
    header: "Created",
    cell: (row: Business) => (
      <span className="text-muted-foreground">{formatDate(row.createdAt)}</span>
    ),
  },
];

export default function BusinessesPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Businesses"
        description="Manage your autonomous business portfolio."
      >
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          New Business
        </Button>
      </PageHeader>

      <Card>
        <CardContent className="p-0">
          <DataTable columns={columns} data={businesses} />
        </CardContent>
      </Card>
    </div>
  );
}
