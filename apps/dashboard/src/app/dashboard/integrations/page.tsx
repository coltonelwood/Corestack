import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { StatusDot } from "@/components/ui/status-dot";
import { EmptyState } from "@/components/state/empty";
import { formatDateTime } from "@/lib/utils";
import { createDataClient } from "@/lib/supabase/data";
import {
  Zap, CreditCard, ShoppingBag, Megaphone, Search as SearchIcon,
  Mail, MessageSquare, Lock, Settings2, AlertTriangle,
} from "lucide-react";

const iconMap: Record<string, React.ElementType> = {
  openai: Zap,
  anthropic: Zap,
  stripe: CreditCard,
  meta_ads: Megaphone,
  google_ads: SearchIcon,
  shopify: ShoppingBag,
  email: Mail,
  sms: MessageSquare,
};

const categoryLabel: Record<string, string> = {
  ai: "AI Providers",
  payments: "Payments",
  advertising: "Advertising",
  ecommerce: "E-Commerce",
  messaging: "Messaging",
};

const statusConfig: Record<string, { variant: "success" | "warning" | "destructive" | "secondary"; label: string }> = {
  connected: { variant: "success", label: "Connected" },
  error: { variant: "destructive", label: "Error" },
  not_configured: { variant: "secondary", label: "Not configured" },
};

interface Connection {
  provider: string;
  display_name: string;
  category: string;
  description: string;
  source: string;
  enabled: boolean;
  status: string;
  has_credential: boolean;
  masked_key: string;
  config: Record<string, unknown>;
  last_tested_at: string | null;
  last_error: string | null;
}

// Provider catalog — displayed even if no DB row exists
const PROVIDER_CATALOG: Connection[] = [
  { provider: "openai", display_name: "OpenAI", category: "ai", description: "GPT models for decisioning and analysis.", source: "env", enabled: false, status: "not_configured", has_credential: false, masked_key: "", config: {}, last_tested_at: null, last_error: null },
  { provider: "anthropic", display_name: "Anthropic", category: "ai", description: "Claude models for content and creative tasks.", source: "env", enabled: false, status: "not_configured", has_credential: false, masked_key: "", config: {}, last_tested_at: null, last_error: null },
  { provider: "stripe", display_name: "Stripe", category: "payments", description: "Payment processing and revenue tracking.", source: "user", enabled: false, status: "not_configured", has_credential: false, masked_key: "", config: {}, last_tested_at: null, last_error: null },
  { provider: "meta_ads", display_name: "Meta Ads", category: "advertising", description: "Facebook and Instagram campaign management.", source: "user", enabled: false, status: "not_configured", has_credential: false, masked_key: "", config: {}, last_tested_at: null, last_error: null },
  { provider: "google_ads", display_name: "Google Ads", category: "advertising", description: "Google search and display campaigns.", source: "user", enabled: false, status: "not_configured", has_credential: false, masked_key: "", config: {}, last_tested_at: null, last_error: null },
  { provider: "shopify", display_name: "Shopify", category: "ecommerce", description: "E-commerce storefront management.", source: "user", enabled: false, status: "not_configured", has_credential: false, masked_key: "", config: {}, last_tested_at: null, last_error: null },
  { provider: "email", display_name: "Email Provider", category: "messaging", description: "Transactional and marketing email.", source: "user", enabled: false, status: "not_configured", has_credential: false, masked_key: "", config: {}, last_tested_at: null, last_error: null },
  { provider: "sms", display_name: "SMS Provider", category: "messaging", description: "SMS notifications and marketing.", source: "user", enabled: false, status: "not_configured", has_credential: false, masked_key: "", config: {}, last_tested_at: null, last_error: null },
];

async function getConnections(): Promise<Connection[]> {
  // Try to load from DB; fall back to catalog defaults
  try {
    const supabase = createDataClient();
    const { data } = await supabase
      .from("integration_connections")
      .select("*")
      .order("provider");

    if (!data || data.length === 0) return PROVIDER_CATALOG;

    const dbMap = new Map(data.map((r) => [r.provider, r]));
    return PROVIDER_CATALOG.map((p) => {
      const row = dbMap.get(p.provider);
      if (!row) return p;
      return {
        ...p,
        enabled: row.enabled,
        status: row.status,
        has_credential: !!row.masked_key,
        masked_key: row.masked_key ?? "",
        config: (row.config as Record<string, unknown>) ?? {},
        last_tested_at: row.last_tested_at,
        last_error: row.last_error,
      };
    });
  } catch {
    return PROVIDER_CATALOG;
  }
}

export default async function IntegrationsPage() {
  const connections = await getConnections();
  const connectedCount = connections.filter((c) => c.status === "connected").length;

  // Group by category
  const grouped = connections.reduce<Record<string, Connection[]>>((acc, c) => {
    (acc[c.category] = acc[c.category] || []).push(c);
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      <PageHeader
        title="Integrations"
        description="Manage external service connections."
        badge={connectedCount > 0 ? <Badge variant="success">{connectedCount} connected</Badge> : undefined}
      />

      <div className="space-y-8 max-w-4xl">
        {Object.entries(grouped).map(([category, providers]) => (
          <div key={category}>
            <h2 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3">
              {categoryLabel[category] ?? category}
            </h2>
            <div className="grid gap-3 sm:grid-cols-2">
              {providers.map((conn) => {
                const Icon = iconMap[conn.provider] ?? Settings2;
                const sc = statusConfig[conn.status] ?? statusConfig.not_configured;

                return (
                  <Card key={conn.provider}>
                    <CardContent className="px-5 py-4">
                      <div className="flex items-start gap-3">
                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-muted">
                          <Icon className="h-5 w-5 text-muted-foreground" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <p className="text-sm font-medium">{conn.display_name}</p>
                            <Badge variant={sc.variant}>
                              <StatusDot status={conn.status} className="mr-1.5" />
                              {sc.label}
                            </Badge>
                          </div>
                          <p className="text-xs text-muted-foreground mt-0.5">{conn.description}</p>

                          {/* Credential info */}
                          <div className="mt-3 flex items-center gap-3 text-xs">
                            {conn.source === "env" ? (
                              <span className="flex items-center gap-1 text-muted-foreground">
                                <Lock className="h-3 w-3" />
                                Environment variable
                              </span>
                            ) : conn.has_credential ? (
                              <span className="font-mono text-muted-foreground">{conn.masked_key}</span>
                            ) : (
                              <span className="text-muted-foreground">No credential configured</span>
                            )}
                          </div>

                          {/* Last tested / error */}
                          {conn.last_error && (
                            <p className="mt-2 flex items-center gap-1 text-xs text-destructive">
                              <AlertTriangle className="h-3 w-3" />
                              {conn.last_error}
                            </p>
                          )}
                          {conn.last_tested_at && !conn.last_error && (
                            <p className="mt-2 text-xs text-muted-foreground">
                              Last tested: {formatDateTime(conn.last_tested_at)}
                            </p>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
