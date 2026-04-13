/**
 * Role-based access control — shared between frontend and backend.
 *
 * Roles: owner > admin > operator > analyst > viewer
 *
 * This module is the single source of truth for what each role can do.
 * The backend enforces these checks via require_role(). The frontend
 * uses them for UI visibility and action gating.
 */

export const ROLES = ["owner", "admin", "operator", "analyst", "viewer"] as const;
export type Role = (typeof ROLES)[number];

export type Permission =
  // Business data
  | "businesses:read"
  | "businesses:write"
  | "products:read"
  | "products:write"
  | "campaigns:read"
  | "campaigns:write"
  // Automation
  | "tasks:read"
  | "tasks:write"
  | "agent_runs:read"
  | "workflows:read"
  | "workflows:execute"
  | "approvals:read"
  | "approvals:decide"
  // AI
  | "ai:read"
  | "ai:execute"
  // Integrations
  | "integrations:read"
  | "integrations:manage"
  | "integrations:dispatch"
  // System
  | "settings:read"
  | "settings:write"
  | "audit_logs:read"
  | "memory:read"
  | "memory:write";

/**
 * Permission matrix. Each role gets the listed permissions.
 * Higher roles inherit everything from lower roles implicitly
 * via the ROLE_PERMISSIONS map — no inheritance chain needed.
 */
const ROLE_PERMISSIONS: Record<Role, readonly Permission[]> = {
  owner: [
    "businesses:read", "businesses:write",
    "products:read", "products:write",
    "campaigns:read", "campaigns:write",
    "tasks:read", "tasks:write",
    "agent_runs:read",
    "workflows:read", "workflows:execute",
    "approvals:read", "approvals:decide",
    "ai:read", "ai:execute",
    "integrations:read", "integrations:manage", "integrations:dispatch",
    "settings:read", "settings:write",
    "audit_logs:read",
    "memory:read", "memory:write",
  ],
  admin: [
    "businesses:read", "businesses:write",
    "products:read", "products:write",
    "campaigns:read", "campaigns:write",
    "tasks:read", "tasks:write",
    "agent_runs:read",
    "workflows:read", "workflows:execute",
    "approvals:read", "approvals:decide",
    "ai:read", "ai:execute",
    "integrations:read", "integrations:manage", "integrations:dispatch",
    "settings:read", "settings:write",
    "audit_logs:read",
    "memory:read", "memory:write",
  ],
  operator: [
    "businesses:read",
    "products:read", "products:write",
    "campaigns:read", "campaigns:write",
    "tasks:read", "tasks:write",
    "agent_runs:read",
    "workflows:read", "workflows:execute",
    "approvals:read",
    "ai:read", "ai:execute",
    "integrations:read", "integrations:dispatch",
    "settings:read",
    "audit_logs:read",
    "memory:read",
  ],
  analyst: [
    "businesses:read",
    "products:read",
    "campaigns:read",
    "tasks:read",
    "agent_runs:read",
    "workflows:read",
    "approvals:read",
    "ai:read",
    "integrations:read",
    "audit_logs:read",
    "memory:read",
  ],
  viewer: [
    "businesses:read",
    "products:read",
    "campaigns:read",
    "tasks:read",
    "agent_runs:read",
    "workflows:read",
  ],
};

/** Check if a role has a specific permission. */
export function hasPermission(role: Role, permission: Permission): boolean {
  return ROLE_PERMISSIONS[role]?.includes(permission) ?? false;
}

/** Check if a role has ALL of the listed permissions. */
export function hasAllPermissions(role: Role, permissions: Permission[]): boolean {
  return permissions.every((p) => hasPermission(role, p));
}

/** Check if a role has ANY of the listed permissions. */
export function hasAnyPermission(role: Role, permissions: Permission[]): boolean {
  return permissions.some((p) => hasPermission(role, p));
}

/** Get all permissions for a role. */
export function getPermissions(role: Role): readonly Permission[] {
  return ROLE_PERMISSIONS[role] ?? [];
}

/** Check if a string is a valid role. */
export function isValidRole(value: string): value is Role {
  return ROLES.includes(value as Role);
}

/** Role display labels. */
export const ROLE_LABELS: Record<Role, string> = {
  owner: "Owner",
  admin: "Admin",
  operator: "Operator",
  analyst: "Analyst",
  viewer: "Viewer",
};
