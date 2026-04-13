import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar } from "@/components/ui/avatar";
import { recentActivity } from "@/data/seed";
import { formatDateTime } from "@/lib/utils";

const agentInitials: Record<string, string> = {
  "Ads Manager": "AM",
  "Analytics Agent": "AA",
  "Content Writer": "CW",
  "Operations Agent": "OA",
  "Research Analyst": "RA",
  "Outreach Agent": "OT",
};

export function ActivityFeed() {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Agent Activity</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {recentActivity.map((item) => (
            <div key={item.id} className="flex items-start gap-3">
              <Avatar
                fallback={agentInitials[item.agent] ?? "AG"}
                size="sm"
              />
              <div className="flex-1 min-w-0">
                <p className="text-sm">
                  <span className="font-medium">{item.agent}</span>{" "}
                  <span className="text-muted-foreground">{item.action}</span>{" "}
                  <span className="font-medium">{item.target}</span>
                </p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {formatDateTime(item.timestamp)}
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
