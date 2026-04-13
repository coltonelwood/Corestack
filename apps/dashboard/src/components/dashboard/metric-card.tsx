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
    <Card className="relative overflow-hidden">
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">{title}</p>
            <p className="text-3xl font-bold tracking-tight">{value}</p>
          </div>
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
            <Icon className="h-5 w-5 text-primary" />
          </div>
        </div>
        <div className="mt-3 flex items-center gap-1.5 text-xs">
          {changeType === "positive" && (
            <span className="flex items-center gap-0.5 rounded-full bg-emerald-50 px-1.5 py-0.5 font-medium text-emerald-700">
              <TrendingUp className="h-3 w-3" />
              {change}
            </span>
          )}
          {changeType === "negative" && (
            <span className="flex items-center gap-0.5 rounded-full bg-red-50 px-1.5 py-0.5 font-medium text-red-600">
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
      </CardContent>
    </Card>
  );
}
