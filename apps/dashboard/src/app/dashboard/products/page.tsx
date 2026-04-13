import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { EmptyState } from "@/components/state/empty";
import { formatCurrency, formatDate } from "@/lib/utils";
import { getProducts } from "@/app/actions/products";
import { getBusinesses } from "@/app/actions/businesses";
import { ProductPageActions } from "./actions";

type ProductWithBiz = Awaited<ReturnType<typeof getProducts>>[number];

const statusVariant: Record<string, "success" | "secondary" | "outline"> = {
  active: "success",
  draft: "secondary",
  archived: "outline",
};

const columns = [
  {
    header: "Product",
    cell: (row: ProductWithBiz) => (
      <div>
        <p className="font-medium">{row.name}</p>
        <p className="text-xs text-muted-foreground">
          {(row.businesses as { name: string } | null)?.name ?? "—"}
        </p>
      </div>
    ),
  },
  {
    header: "Category",
    cell: (row: ProductWithBiz) => (
      <span className="text-muted-foreground">{row.category ?? "—"}</span>
    ),
  },
  {
    header: "Status",
    cell: (row: ProductWithBiz) => (
      <Badge variant={statusVariant[row.status] ?? "secondary"}>{row.status}</Badge>
    ),
  },
  {
    header: "Price",
    cell: (row: ProductWithBiz) => (
      <span className="font-medium">{formatCurrency(row.price_cents / 100)}</span>
    ),
    className: "text-right",
  },
  {
    header: "Inventory",
    cell: (row: ProductWithBiz) => (
      <span className="text-muted-foreground">{row.inventory.toLocaleString()}</span>
    ),
    className: "text-right",
  },
  {
    header: "Sales",
    cell: (row: ProductWithBiz) => (
      <span className="font-medium">{row.sales_count.toLocaleString()}</span>
    ),
    className: "text-right",
  },
  {
    header: "Created",
    cell: (row: ProductWithBiz) => (
      <span className="text-muted-foreground">{formatDate(row.created_at)}</span>
    ),
  },
];

export default async function ProductsPage() {
  const [products, businesses] = await Promise.all([
    getProducts(),
    getBusinesses(),
  ]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Products"
        description="All products across your business portfolio."
      >
        <ProductPageActions businesses={businesses} />
      </PageHeader>

      {products.length === 0 ? (
        <Card>
          <CardContent className="p-0">
            <EmptyState
              title="No products yet"
              description="Add your first product to one of your businesses."
            />
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0">
            <DataTable columns={columns} data={products} />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
