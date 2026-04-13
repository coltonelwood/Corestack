import { createClient as createSupabaseClient } from "@supabase/supabase-js";
import type { Database } from "@abf/db";

/**
 * Typed Supabase client for data queries in server actions.
 * Uses @supabase/supabase-js directly for full Database generic support.
 */
export function createDataClient() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!url || !key) {
    throw new Error(
      "Missing NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY. " +
      "See apps/dashboard/.env.example."
    );
  }

  return createSupabaseClient<Database>(url, key);
}
