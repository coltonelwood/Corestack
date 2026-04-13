import { Card } from "@/components/ui/card";
import {
  DollarSign,
  TrendingDown,
  TrendingUp,
  Building2,
  Megaphone,
  ShieldCheck,
  Minus,
} from "lucide-react";

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
      <div className="px-5 py-4">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs font-medium text-muted-foreground">{title}</p>
            <p className="mt-1.5 text-2xl font-bold tabular-nums tracking-tight">{value}</p>
          </div>
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/8">
            <Icon className="h-4 w-4 text-primary" />
          </div>
        </div>
        <div className="mt-2 flex items-center gap-1.5 text-xs">
          {changeType === "positive" && (
            <span className="flex items-center gap-0.5 font-medium text-emerald-600">
              <TrendingUp className="h-3 w-3" />
              {change}
            </span>
          )}
          {changeType === "negative" && (
            <span className="flex items-center gap-0.5 font-medium text-red-600">
              <TrendingDown className="h-3 w-3" />
              {change}
            </span>
          )}
          {changeType === "neutral" && (
            <span className="flex items-center gap-0.5 text-muted-foreground">
              <Minus className="h-3 w-3" />
              {change}
            </span>
          )}
        </div>
      </div>
    </Card>
  );
}
