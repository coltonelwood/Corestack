/**
 * @abf/core — shared types and utilities for the ABF platform.
 */

export type AgentStatus = "idle" | "running" | "completed" | "failed";

export type WorkflowStatus = "draft" | "active" | "paused" | "archived";

export interface Agent {
  id: string;
  name: string;
  description: string;
  status: AgentStatus;
  createdAt: string;
  updatedAt: string;
}

export interface Workflow {
  id: string;
  name: string;
  description: string;
  status: WorkflowStatus;
  steps: WorkflowStep[];
  createdAt: string;
  updatedAt: string;
}

export interface WorkflowStep {
  id: string;
  name: string;
  agentId: string;
  order: number;
}

// RBAC
export {
  ROLES,
  ROLE_LABELS,
  type Role,
  type Permission,
  hasPermission,
  hasAllPermissions,
  hasAnyPermission,
  getPermissions,
  isValidRole,
} from "./rbac";
