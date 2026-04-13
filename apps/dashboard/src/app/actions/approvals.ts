"use server";

import { revalidatePath } from "next/cache";
import { createDataClient } from "@/lib/supabase/data";

export async function getApprovals() {
  const supabase = createDataClient();
  const { data, error } = await supabase
    .from("approvals")
    .select("*, businesses(name)")
    .order("created_at", { ascending: false });

  if (error) throw new Error(error.message);
  return data;
}

export async function approveApproval(id: string) {
  const supabase = createDataClient();
  const { error } = await supabase
    .from("approvals")
    .update({
      status: "approved" as const,
      reviewed_by: "admin",
      reviewed_at: new Date().toISOString(),
    })
    .eq("id", id);

  if (error) return { error: error.message };

  revalidatePath("/dashboard/approvals");
  revalidatePath("/dashboard");
  return { success: true };
}

export async function rejectApproval(id: string) {
  const supabase = createDataClient();
  const { error } = await supabase
    .from("approvals")
    .update({
      status: "rejected" as const,
      reviewed_by: "admin",
      reviewed_at: new Date().toISOString(),
    })
    .eq("id", id);

  if (error) return { error: error.message };

  revalidatePath("/dashboard/approvals");
  revalidatePath("/dashboard");
  return { success: true };
}
