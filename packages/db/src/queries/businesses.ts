import type { SupabaseClient } from "@supabase/supabase-js";
import type { Database, BusinessInsert, BusinessUpdate, BusinessStatus } from "../types/database";

type Client = SupabaseClient<Database>;

export function listBusinesses(client: Client, status?: BusinessStatus) {
  let query = client
    .from("businesses")
    .select("*")
    .order("created_at", { ascending: false });

  if (status) {
    query = query.eq("status", status);
  }

  return query;
}

export function getBusinessById(client: Client, id: string) {
  return client.from("businesses").select("*").eq("id", id).single();
}

export function createBusiness(client: Client, data: BusinessInsert) {
  return client.from("businesses").insert(data).select().single();
}

export function updateBusiness(
  client: Client,
  id: string,
  data: BusinessUpdate
) {
  return client.from("businesses").update(data).eq("id", id).select().single();
}

export function deleteBusiness(client: Client, id: string) {
  return client.from("businesses").delete().eq("id", id);
}
