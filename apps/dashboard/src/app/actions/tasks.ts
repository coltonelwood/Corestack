"use server";

import { revalidatePath } from "next/cache";
import { createDataClient } from "@/lib/supabase/data";
import type { TaskPriority } from "@abf/db";

export async function getTasks() {
  const supabase = createDataClient();
  const { data, error } = await supabase
    .from("tasks")
    .select("*, businesses(name)")
    .order("created_at", { ascending: false });

  if (error) throw new Error(error.message);
  return data;
}

export async function createTask(formData: FormData) {
  const supabase = createDataClient();

  const { data, error } = await supabase
    .from("tasks")
    .insert({
      business_id: formData.get("business_id") as string,
      title: formData.get("title") as string,
      description: (formData.get("description") as string) || null,
      priority: (formData.get("priority") as TaskPriority) || "medium",
      assigned_agent: (formData.get("assigned_agent") as string) || null,
      status: "pending" as const,
    })
    .select()
    .single();

  if (error) return { error: error.message };

  revalidatePath("/dashboard/tasks");
  revalidatePath("/dashboard");
  return { data };
}
