import { createClient as createSupabaseClient } from "@supabase/supabase-js";
import type { Database } from "@abf/db";

/**
 * Typed Supabase client for data queries in server actions.
 * Uses @supabase/supabase-js directly for full Database generic support.
 * Auth is handled at the middleware layer — this client uses the anon key.
 */
export function createDataClient() {
  return createSupabaseClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}
