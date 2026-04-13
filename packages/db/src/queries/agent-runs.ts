import type { SupabaseClient } from "@supabase/supabase-js";
import type {
  Database,
  AgentRunInsert,
  AgentRunUpdate,
  AgentRunStatus,
  AgentType,
  Json,
} from "../types/database";

type Client = SupabaseClient<Database>;

export function listAgentRuns(
  client: Client,
  filters?: { businessId?: string; status?: AgentRunStatus; agentType?: AgentType }
) {
  let query = client
    .from("agent_runs")
    .select("*, businesses(name), tasks(title)")
    .order("started_at", { ascending: false });

  if (filters?.businessId) {
    query = query.eq("business_id", filters.businessId);
  }
  if (filters?.status) {
    query = query.eq("status", filters.status);
  }
  if (filters?.agentType) {
    query = query.eq("agent_type", filters.agentType);
  }

  return query;
}

export function getAgentRunById(client: Client, id: string) {
  return client
    .from("agent_runs")
    .select("*, businesses(name), tasks(title)")
    .eq("id", id)
    .single();
}

export function createAgentRun(client: Client, data: AgentRunInsert) {
  return client.from("agent_runs").insert(data).select().single();
}

export function updateAgentRun(
  client: Client,
  id: string,
  data: AgentRunUpdate
) {
  return client.from("agent_runs").update(data).eq("id", id).select().single();
}

export function completeAgentRun(
  client: Client,
  id: string,
  output: Json,
  stats: { duration_ms: number; tokens_used: number; cost_cents: number }
) {
  const update: AgentRunUpdate = {
    status: "completed" as const,
    output_payload: output,
    completed_at: new Date().toISOString(),
    ...stats,
  };
  return client.from("agent_runs").update(update).eq("id", id).select().single();
}

export function failAgentRun(
  client: Client,
  id: string,
  errorMessage: string,
  stats: { duration_ms: number; tokens_used: number; cost_cents: number }
) {
  const update: AgentRunUpdate = {
    status: "failed" as const,
    error_message: errorMessage,
    completed_at: new Date().toISOString(),
    ...stats,
  };
  return client.from("agent_runs").update(update).eq("id", id).select().single();
}
