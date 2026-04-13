"use server";

import { revalidatePath } from "next/cache";
import { createDataClient } from "@/lib/supabase/data";

export async function getProducts() {
  const supabase = createDataClient();
  const { data, error } = await supabase
    .from("products")
    .select("*, businesses(name)")
    .order("created_at", { ascending: false });

  if (error) throw new Error(error.message);
  return data;
}

export async function createProduct(formData: FormData) {
  const supabase = createDataClient();

  const { data, error } = await supabase
    .from("products")
    .insert({
      business_id: formData.get("business_id") as string,
      name: formData.get("name") as string,
      description: (formData.get("description") as string) || null,
      category: (formData.get("category") as string) || null,
      price_cents: Math.round(parseFloat(formData.get("price") as string) * 100),
      cost_cents: Math.round(parseFloat((formData.get("cost") as string) || "0") * 100),
      status: "draft" as const,
      inventory: parseInt((formData.get("inventory") as string) || "0", 10),
    })
    .select()
    .single();

  if (error) return { error: error.message };

  revalidatePath("/dashboard/products");
  revalidatePath("/dashboard");
  return { data };
}
