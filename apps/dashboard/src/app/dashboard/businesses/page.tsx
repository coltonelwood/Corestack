import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { StatusDot } from "@/components/ui/status-dot";
import { EmptyState } from "@/components/state/empty";
import { formatCurrency, formatDate } from "@/lib/utils";
import { getBusinesses } from "@/app/actions/businesses";
import { BusinessPageActions } from "./actions";
import type { BusinessRow } from "@abf/db";

const statusVariant: Record<string, "success" | "warning" | "secondary"> = {
  active: "success",
  paused: "warning",
  setup: "secondary",
};

const columns = [
  {
    header: "Business",
    cell: (row: BusinessRow) => (
      <div>
        <p className="font-medium">{row.name}</p>
        <p className="text-xs text-muted-foreground">{row.domain ?? "—"}</p>
      </div>
    ),
  },
  {
    header: "Status",
    cell: (row: BusinessRow) => (
      <Badge variant={statusVariant[row.status] ?? "secondary"}>
        <StatusDot status={row.status} className="mr-1.5" />
        {row.status}
      </Badge>
    ),
  },
  {
    header: "Description",
    cell: (row: BusinessRow) => (
      <span className="text-sm text-muted-foreground truncate block max-w-xs">
        {row.description ?? "—"}
      </span>
    ),
  },
  {
    header: "Created",
    cell: (row: BusinessRow) => (
      <span className="text-muted-foreground">{formatDate(row.created_at)}</span>
    ),
  },
];

export default async function BusinessesPage() {
  const businesses = await getBusinesses();

  return (
    <div className="space-y-6">
      <PageHeader
        title="Businesses"
        description="Manage your autonomous business portfolio."
      >
        <BusinessPageActions />
      </PageHeader>

      {businesses.length === 0 ? (
        <Card>
          <CardContent className="p-0">
            <EmptyState
              title="No businesses yet"
              description="Create your first autonomous business to get started."
            />
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0">
            <DataTable columns={columns} data={businesses} />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
