import type { SupabaseClient } from "@supabase/supabase-js";
import type { Database, ProductInsert, ProductUpdate } from "../types/database";

type Client = SupabaseClient<Database>;

export function listProducts(client: Client, businessId?: string) {
  let query = client
    .from("products")
    .select("*, businesses(name)")
    .order("created_at", { ascending: false });

  if (businessId) {
    query = query.eq("business_id", businessId);
  }

  return query;
}

export function getProductById(client: Client, id: string) {
  return client
    .from("products")
    .select("*, businesses(name)")
    .eq("id", id)
    .single();
}

export function createProduct(client: Client, data: ProductInsert) {
  return client.from("products").insert(data).select().single();
}

export function updateProduct(
  client: Client,
  id: string,
  data: ProductUpdate
) {
  return client.from("products").update(data).eq("id", id).select().single();
}

export function deleteProduct(client: Client, id: string) {
  return client.from("products").delete().eq("id", id);
}
