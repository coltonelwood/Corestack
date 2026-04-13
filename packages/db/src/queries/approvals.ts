import type { SupabaseClient } from "@supabase/supabase-js";
import type {
  Database,
  ApprovalInsert,
  ApprovalUpdate,
  ApprovalStatus,
} from "../types/database";

type Client = SupabaseClient<Database>;

export function listApprovals(
  client: Client,
  filters?: { businessId?: string; status?: ApprovalStatus }
) {
  let query = client
    .from("approvals")
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

export function getApprovalById(client: Client, id: string) {
  return client
    .from("approvals")
    .select("*, businesses(name)")
    .eq("id", id)
    .single();
}

export function createApproval(client: Client, data: ApprovalInsert) {
  return client.from("approvals").insert(data).select().single();
}

export function approveApproval(
  client: Client,
  id: string,
  reviewedBy: string
) {
  const update: ApprovalUpdate = {
    status: "approved" as const,
    reviewed_by: reviewedBy,
    reviewed_at: new Date().toISOString(),
  };
  return client.from("approvals").update(update).eq("id", id).select().single();
}

export function rejectApproval(
  client: Client,
  id: string,
  reviewedBy: string
) {
  const update: ApprovalUpdate = {
    status: "rejected" as const,
    reviewed_by: reviewedBy,
    reviewed_at: new Date().toISOString(),
  };
  return client.from("approvals").update(update).eq("id", id).select().single();
}
