"use server";

import { createDataClient } from "@/lib/supabase/data";

export async function getWorkflowRuns() {
  const supabase = createDataClient();
  const { data, error } = await supabase
    .from("workflow_runs")
    .select("*")
    .order("created_at", { ascending: false });

  if (error) throw new Error(error.message);
  return data ?? [];
}

export async function getWorkflowRun(id: string) {
  const supabase = createDataClient();

  const { data: run, error: runErr } = await supabase
    .from("workflow_runs")
    .select("*")
    .eq("id", id)
    .single();

  if (runErr) throw new Error(runErr.message);

  const { data: steps, error: stepsErr } = await supabase
    .from("workflow_step_runs")
    .select("*")
    .eq("workflow_run_id", id)
    .order("created_at", { ascending: true });

  if (stepsErr) throw new Error(stepsErr.message);

  return { ...run, steps: steps ?? [] };
}
