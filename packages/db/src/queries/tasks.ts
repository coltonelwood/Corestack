import type { SupabaseClient } from "@supabase/supabase-js";
import type {
  Database,
  TaskInsert,
  TaskUpdate,
  TaskStatus,
  Json,
} from "../types/database";

type Client = SupabaseClient<Database>;

export function listTasks(
  client: Client,
  filters?: { businessId?: string; status?: TaskStatus; assignedAgent?: string }
) {
  let query = client
    .from("tasks")
    .select("*, businesses(name)")
    .order("created_at", { ascending: false });

  if (filters?.businessId) {
    query = query.eq("business_id", filters.businessId);
  }
  if (filters?.status) {
    query = query.eq("status", filters.status);
  }
  if (filters?.assignedAgent) {
    query = query.eq("assigned_agent", filters.assignedAgent);
  }

  return query;
}

export function getTaskById(client: Client, id: string) {
  return client
    .from("tasks")
    .select("*, businesses(name)")
    .eq("id", id)
    .single();
}

export function createTask(client: Client, data: TaskInsert) {
  return client.from("tasks").insert(data).select().single();
}

export function updateTask(client: Client, id: string, data: TaskUpdate) {
  return client.from("tasks").update(data).eq("id", id).select().single();
}

export function completeTask(
  client: Client,
  id: string,
  result: Json
) {
  const update: TaskUpdate = {
    status: "completed" as const,
    result,
    completed_at: new Date().toISOString(),
  };
  return client.from("tasks").update(update).eq("id", id).select().single();
}

export function failTask(client: Client, id: string, error: string) {
  const update: TaskUpdate = {
    status: "failed" as const,
    result: { error },
    completed_at: new Date().toISOString(),
  };
  return client.from("tasks").update(update).eq("id", id).select().single();
}
