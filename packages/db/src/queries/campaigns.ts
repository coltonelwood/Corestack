import type { SupabaseClient } from "@supabase/supabase-js";
import type {
  Database,
  CampaignInsert,
  CampaignUpdate,
  CampaignStatus,
} from "../types/database";

type Client = SupabaseClient<Database>;

export function listCampaigns(
  client: Client,
  filters?: { businessId?: string; status?: CampaignStatus }
) {
  let query = client
    .from("campaigns")
    .select("*, businesses(name)")
    .order("created_at", { ascending: false });

  if (filters?.businessId) {
    query = query.eq("business_id", filters.businessId);
  }
  if (filters?.status) {
    query = query.eq("status", filters.status);
  }

  return query;
}

export function getCampaignById(client: Client, id: string) {
  return client
    .from("campaigns")
    .select("*, businesses(name), products(name)")
    .eq("id", id)
    .single();
}

export function createCampaign(client: Client, data: CampaignInsert) {
  return client.from("campaigns").insert(data).select().single();
}

export function updateCampaign(
  client: Client,
  id: string,
  data: CampaignUpdate
) {
  return client.from("campaigns").update(data).eq("id", id).select().single();
}
