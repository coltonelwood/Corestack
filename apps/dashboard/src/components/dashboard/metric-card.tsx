import { Card, CardContent } from "@/components/ui/card";
import {
  DollarSign,
  TrendingDown,
  TrendingUp,
  Building2,
  Megaphone,
  ShieldCheck,
  Minus,
} from "lucide-react";
import { cn } from "@/lib/utils";

const iconMap: Record<string, React.ElementType> = {
  revenue: DollarSign,
  spend: TrendingDown,
  profit: TrendingUp,
  businesses: Building2,
  campaigns: Megaphone,
  approvals: ShieldCheck,
};

interface MetricCardProps {
  title: string;
  value: string;
  change: string;
  changeType: "positive" | "negative" | "neutral";
  icon: string;
}

export function MetricCard({
  title,
  value,
  change,
  changeType,
  icon,
}: MetricCardProps) {
  const Icon = iconMap[icon] ?? DollarSign;

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
            <Icon className="h-4 w-4 text-primary" />
          </div>
        </div>
        <div className="mt-3">
          <p className="text-2xl font-bold tracking-tight">{value}</p>
          <div className="mt-1 flex items-center gap-1 text-xs">
            {changeType === "positive" && (
              <TrendingUp className="h-3 w-3 text-emerald-600" />
            )}
            {changeType === "negative" && (
              <TrendingDown className="h-3 w-3 text-red-500" />
            )}
            {changeType === "neutral" && (
              <Minus className="h-3 w-3 text-muted-foreground" />
            )}
            <span
              className={cn(
                "font-medium",
                changeType === "positive" && "text-emerald-600",
                changeType === "negative" && "text-red-500",
                changeType === "neutral" && "text-muted-foreground"
              )}
            >
              {change}
            </span>
            <span className="text-muted-foreground">vs last month</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
