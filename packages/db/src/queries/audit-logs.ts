import type { SupabaseClient } from "@supabase/supabase-js";
import type { Database, AuditLogInsert } from "../types/database";

type Client = SupabaseClient<Database>;

export function listAuditLogs(
  client: Client,
  filters?: {
    businessId?: string;
    entityType?: string;
    entityId?: string;
    limit?: number;
  }
) {
  let query = client
    .from("audit_logs")
    .select("*")
    .order("created_at", { ascending: false });

  if (filters?.businessId) {
    query = query.eq("business_id", filters.businessId);
  }
  if (filters?.entityType) {
    query = query.eq("entity_type", filters.entityType);
  }
  if (filters?.entityId) {
    query = query.eq("entity_id", filters.entityId);
  }
  if (filters?.limit) {
    query = query.limit(filters.limit);
  }

  return query;
}

export function createAuditLog(client: Client, data: AuditLogInsert) {
  return client.from("audit_logs").insert(data).select().single();
}
