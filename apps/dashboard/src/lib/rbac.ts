/**
 * Frontend RBAC utilities.
 *
 * Re-exports the shared permission checks from @abf/core and adds
 * a server-side function to load the current user's role.
 */

import { type Role, type Permission, hasPermission, ROLE_LABELS } from "@abf/core";
import { createDataClient } from "@/lib/supabase/data";

export type { Role, Permission };
export { hasPermission, ROLE_LABELS };

const DEFAULT_ROLE: Role = "viewer";

/**
 * Load the current user's role from the user_roles table.
 * Call this from server components or server actions.
 */
export async function getUserRole(userId: string): Promise<Role> {
  try {
    const supabase = createDataClient();
    const { data } = await supabase
      .from("user_roles")
      .select("role")
      .eq("user_id", userId)
      .single();

    if (data?.role) return data.role as Role;
  } catch {
    // Table might not exist yet, or user has no role row
  }
  return DEFAULT_ROLE;
}

/** Navigation items with their required permissions. */
export const NAV_PERMISSIONS: Record<string, Permission | null> = {
  "/dashboard": null,
  "/dashboard/businesses": "businesses:read",
  "/dashboard/products": "products:read",
  "/dashboard/campaigns": "campaigns:read",
  "/dashboard/tasks": "tasks:read",
  "/dashboard/agent-runs": "agent_runs:read",
  "/dashboard/workflows": "workflows:read",
  "/dashboard/approvals": "approvals:read",
  "/dashboard/settings": "settings:read",
};

/** Check if a role can access a given route. */
export function canAccessRoute(role: Role, href: string): boolean {
  const permission = NAV_PERMISSIONS[href];
  if (permission === null || permission === undefined) return true;
  return hasPermission(role, permission);
}
