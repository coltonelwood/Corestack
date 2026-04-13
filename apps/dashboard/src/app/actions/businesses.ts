"use server";

import { revalidatePath } from "next/cache";
import { createDataClient } from "@/lib/supabase/data";

export async function getBusinesses() {
  const supabase = createDataClient();
  const { data, error } = await supabase
    .from("businesses")
    .select("*")
    .order("created_at", { ascending: false });

  if (error) throw new Error(error.message);
  return data;
}

export async function getBusinessById(id: string) {
  const supabase = createDataClient();
  const { data, error } = await supabase
    .from("businesses")
    .select("*")
    .eq("id", id)
    .single();

  if (error) throw new Error(error.message);
  return data;
}

export async function createBusiness(formData: FormData) {
  const supabase = createDataClient();

  const { data, error } = await supabase
    .from("businesses")
    .insert({
      name: formData.get("name") as string,
      domain: (formData.get("domain") as string) || null,
      description: (formData.get("description") as string) || null,
      status: "setup" as const,
    })
    .select()
    .single();

  if (error) return { error: error.message };

  revalidatePath("/dashboard/businesses");
  revalidatePath("/dashboard");
  return { data };
}
