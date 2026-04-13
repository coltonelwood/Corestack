import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { businesses } from "@/data/seed";
import { formatCurrency, cn } from "@/lib/utils";

export function PerformanceSummary() {
  const activeBiz = businesses.filter((b) => b.status === "active");

  return (
    <Card>
      <CardHeader>
        <CardTitle>Business Performance</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {activeBiz.map((biz) => {
            const profit = biz.revenue - biz.spend;
            const margin =
              biz.revenue > 0
                ? Math.round((profit / biz.revenue) * 100)
                : 0;
            const revenuePercent = Math.round(
              (biz.revenue / 300000) * 100
            );

            return (
              <div key={biz.id} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium">{biz.name}</span>
                  <span className="text-muted-foreground">
                    {formatCurrency(biz.revenue)}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex-1 h-2 rounded-full bg-secondary">
                    <div
                      className="h-2 rounded-full bg-primary transition-all"
                      style={{ width: `${Math.min(revenuePercent, 100)}%` }}
                    />
                  </div>
                  <span
                    className={cn(
                      "text-xs font-medium w-10 text-right",
                      margin >= 50
                        ? "text-emerald-600"
                        : margin >= 30
                          ? "text-amber-600"
                          : "text-red-500"
                    )}
                  >
                    {margin}%
                  </span>
                </div>
              </div>
            );
          })}
        </div>
        <div className="mt-4 pt-3 border-t flex items-center justify-between text-xs text-muted-foreground">
          <span>Margin displayed as % of revenue</span>
          <span>Bar relative to $300k target</span>
        </div>
      </CardContent>
    </Card>
  );
}
