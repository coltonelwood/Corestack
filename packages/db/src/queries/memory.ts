import type { SupabaseClient } from "@supabase/supabase-js";
import type { Database, MemoryInsert, MemoryUpdate } from "../types/database";

type Client = SupabaseClient<Database>;

/**
 * Get a single memory entry by its composite key.
 */
export function getMemory(
  client: Client,
  params: {
    businessId: string;
    agentName: string;
    namespace?: string;
    key: string;
  }
) {
  return client
    .from("memory")
    .select("*")
    .eq("business_id", params.businessId)
    .eq("agent_name", params.agentName)
    .eq("namespace", params.namespace ?? "default")
    .eq("key", params.key)
    .single();
}

/**
 * List all memory entries for an agent, optionally within a namespace.
 */
export function listMemory(
  client: Client,
  params: { businessId?: string; agentName: string; namespace?: string }
) {
  let query = client
    .from("memory")
    .select("*")
    .eq("agent_name", params.agentName)
    .order("updated_at", { ascending: false });

  if (params.businessId) {
    query = query.eq("business_id", params.businessId);
  }
  if (params.namespace) {
    query = query.eq("namespace", params.namespace);
  }

  return query;
}

/**
 * Upsert a memory entry. Uses the unique index on
 * (business_id, agent_name, namespace, key).
 */
export function upsertMemory(client: Client, data: MemoryInsert) {
  return client
    .from("memory")
    .upsert(data, {
      onConflict: "business_id,agent_name,namespace,key",
    })
    .select()
    .single();
}

export function updateMemory(
  client: Client,
  id: string,
  data: MemoryUpdate
) {
  return client.from("memory").update(data).eq("id", id).select().single();
}

export function deleteMemory(client: Client, id: string) {
  return client.from("memory").delete().eq("id", id);
}
