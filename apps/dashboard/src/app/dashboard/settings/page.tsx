import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { getUser } from "@/app/actions/auth";

function SettingsSection({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}

function FieldRow({
  label,
  description,
  children,
}: {
  label: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 py-3 border-b last:border-0">
      <div>
        <p className="text-sm font-medium">{label}</p>
        {description && (
          <p className="text-xs text-muted-foreground mt-0.5">{description}</p>
        )}
      </div>
      <div className="sm:w-72">{children}</div>
    </div>
  );
}

export default async function SettingsPage() {
  const user = await getUser();

  return (
    <div className="space-y-6">
      <PageHeader
        title="Settings"
        description="Manage your platform configuration."
      />

      <div className="space-y-6 max-w-3xl">
        <SettingsSection title="Profile" description="Your account details.">
          <div className="space-y-0">
            <FieldRow label="Email">
              <Input defaultValue={user?.email ?? ""} type="email" disabled />
            </FieldRow>
            <FieldRow label="User ID">
              <Input defaultValue={user?.id ?? ""} disabled />
            </FieldRow>
          </div>
        </SettingsSection>

        <SettingsSection
          title="API Keys"
          description="Manage external service credentials."
        >
          <div className="space-y-0">
            <FieldRow label="OpenAI API Key" description="Used for content generation and analysis.">
              <Input type="password" placeholder="sk-..." />
            </FieldRow>
            <FieldRow label="Anthropic API Key" description="Used for agent reasoning and planning.">
              <Input type="password" placeholder="sk-ant-..." />
            </FieldRow>
            <FieldRow label="Meta Marketing API" description="For Meta/Facebook ad management.">
              <Input placeholder="Enter token..." />
            </FieldRow>
            <FieldRow label="Google Ads API" description="For Google Ads campaign management.">
              <Input placeholder="Enter token..." />
            </FieldRow>
          </div>
          <div className="mt-4 flex justify-end">
            <Button>Save Keys</Button>
          </div>
        </SettingsSection>

        <SettingsSection
          title="Notifications"
          description="Configure how you receive alerts."
        >
          <div className="space-y-0">
            <FieldRow label="Email Notifications" description="Receive email alerts for approvals and failures.">
              <Button variant="outline" size="sm">Enabled</Button>
            </FieldRow>
            <FieldRow label="Approval Alerts" description="Get notified when agents request approval.">
              <Button variant="outline" size="sm">Enabled</Button>
            </FieldRow>
            <FieldRow label="Daily Digest" description="Receive a daily summary of all agent activity.">
              <Button variant="outline" size="sm">Disabled</Button>
            </FieldRow>
          </div>
        </SettingsSection>
      </div>
    </div>
  );
}
