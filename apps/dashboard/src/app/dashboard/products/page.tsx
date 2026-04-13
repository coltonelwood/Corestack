import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import { products } from "@/data/seed";
import { formatCurrency, formatDate } from "@/lib/utils";
import { Plus } from "lucide-react";
import type { Product } from "@/types";

const statusVariant: Record<string, "success" | "secondary" | "outline"> = {
  active: "success",
  draft: "secondary",
  archived: "outline",
};

const columns = [
  {
    header: "Product",
    cell: (row: Product) => (
      <div>
        <p className="font-medium">{row.name}</p>
        <p className="text-xs text-muted-foreground">{row.businessName}</p>
      </div>
    ),
  },
  {
    header: "Category",
    cell: (row: Product) => (
      <span className="text-muted-foreground">{row.category}</span>
    ),
  },
  {
    header: "Status",
    cell: (row: Product) => (
      <Badge variant={statusVariant[row.status]}>{row.status}</Badge>
    ),
  },
  {
    header: "Price",
    cell: (row: Product) => (
      <span className="font-medium">{formatCurrency(row.price)}</span>
    ),
    className: "text-right",
  },
  {
    header: "Inventory",
    cell: (row: Product) => (
      <span className="text-muted-foreground">
        {row.inventory.toLocaleString()}
      </span>
    ),
    className: "text-right",
  },
  {
    header: "Sales",
    cell: (row: Product) => (
      <span className="font-medium">{row.sales.toLocaleString()}</span>
    ),
    className: "text-right",
  },
  {
    header: "Created",
    cell: (row: Product) => (
      <span className="text-muted-foreground">{formatDate(row.createdAt)}</span>
    ),
  },
];

export default function ProductsPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Products"
        description="All products across your business portfolio."
      >
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Add Product
        </Button>
      </PageHeader>

      <Card>
        <CardContent className="p-0">
          <DataTable columns={columns} data={products} />
        </CardContent>
      </Card>
    </div>
  );
}
