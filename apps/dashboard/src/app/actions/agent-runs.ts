"use server";

import { createDataClient } from "@/lib/supabase/data";

export async function getAgentRuns() {
  const supabase = createDataClient();
  const { data, error } = await supabase
    .from("agent_runs")
    .select("*, businesses(name), tasks(title)")
    .order("started_at", { ascending: false });

  if (error) throw new Error(error.message);
  return data;
}
