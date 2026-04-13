"use server";

import { revalidatePath } from "next/cache";
import { createDataClient } from "@/lib/supabase/data";
import type { CampaignChannel } from "@abf/db";

export async function getCampaigns() {
  const supabase = createDataClient();
  const { data, error } = await supabase
    .from("campaigns")
    .select("*, businesses(name)")
    .order("created_at", { ascending: false });

  if (error) throw new Error(error.message);
  return data;
}

export async function createCampaign(formData: FormData) {
  const supabase = createDataClient();

  const productId = formData.get("product_id") as string;

  const { data, error } = await supabase
    .from("campaigns")
    .insert({
      business_id: formData.get("business_id") as string,
      name: formData.get("name") as string,
      channel: formData.get("channel") as CampaignChannel,
      status: "draft" as const,
      budget_cents: Math.round(parseFloat(formData.get("budget") as string) * 100),
      start_date: (formData.get("start_date") as string) || null,
      end_date: (formData.get("end_date") as string) || null,
      product_id: productId || null,
    })
    .select()
    .single();

  if (error) return { error: error.message };

  revalidatePath("/dashboard/campaigns");
  revalidatePath("/dashboard");
  return { data };
}
