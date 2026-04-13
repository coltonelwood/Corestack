// Client factories
export { createClient, createServiceClient } from "./client";

// Database types
export type {
  Database,
  Json,
  // Row types
  BusinessRow,
  ProductRow,
  CampaignRow,
  TaskRow,
  AgentRunRow,
  ApprovalRow,
  AuditLogRow,
  MemoryRow,
  // Insert types
  BusinessInsert,
  ProductInsert,
  CampaignInsert,
  TaskInsert,
  AgentRunInsert,
  ApprovalInsert,
  AuditLogInsert,
  MemoryInsert,
  // Update types
  BusinessUpdate,
  ProductUpdate,
  CampaignUpdate,
  TaskUpdate,
  AgentRunUpdate,
  ApprovalUpdate,
  MemoryUpdate,
  // Enum types
  BusinessStatus,
  ProductStatus,
  CampaignChannel,
  CampaignStatus,
  TaskStatus,
  TaskPriority,
  AgentType,
  AgentRunStatus,
  ApprovalType,
  ApprovalStatus,
} from "./types/database";

// Query helpers
export * from "./queries";
