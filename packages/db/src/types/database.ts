/**
 * TypeScript types for the ABF Supabase database schema.
 *
 * These map 1:1 to the Postgres tables defined in migrations/001_initial_schema.sql.
 * Format matches the output of `supabase gen types typescript` so that
 * @supabase/supabase-js generics resolve correctly.
 *
 * All monetary values are stored as integer cents (e.g. 4200 = $42.00).
 */

// ── Enum-like unions ────────────────────────────────────────

export type BusinessStatus = "active" | "paused" | "setup" | "archived";
export type ProductStatus = "active" | "draft" | "archived";
export type CampaignChannel = "google" | "meta" | "tiktok" | "email" | "linkedin" | "other";
export type CampaignStatus = "active" | "paused" | "completed" | "draft";
export type TaskStatus = "pending" | "in_progress" | "completed" | "failed" | "cancelled";
export type TaskPriority = "low" | "medium" | "high" | "critical";
export type AgentType = "research" | "content" | "ads" | "analytics" | "outreach" | "operations";
export type AgentRunStatus = "queued" | "running" | "completed" | "failed";
export type ApprovalType = "campaign_launch" | "budget_increase" | "content_publish" | "product_listing" | "price_change" | "other";
export type ApprovalStatus = "pending" | "approved" | "rejected";

// ── Json helper ─────────────────────────────────────────────

export type Json = string | number | boolean | null | { [key: string]: Json | undefined } | Json[];

// ── Database interface ──────────────────────────────────────

export interface Database {
  public: {
    Tables: {
      businesses: {
        Row: {
          id: string;
          name: string;
          domain: string | null;
          description: string | null;
          status: BusinessStatus;
          metadata: Json;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          name: string;
          domain?: string | null;
          description?: string | null;
          status?: BusinessStatus;
          metadata?: Json;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          name?: string;
          domain?: string | null;
          description?: string | null;
          status?: BusinessStatus;
          metadata?: Json;
          created_at?: string;
          updated_at?: string;
        };
        Relationships: [];
      };
      products: {
        Row: {
          id: string;
          business_id: string;
          name: string;
          description: string | null;
          category: string | null;
          price_cents: number;
          cost_cents: number;
          status: ProductStatus;
          inventory: number;
          sales_count: number;
          metadata: Json;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          business_id: string;
          name: string;
          description?: string | null;
          category?: string | null;
          price_cents?: number;
          cost_cents?: number;
          status?: ProductStatus;
          inventory?: number;
          sales_count?: number;
          metadata?: Json;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          business_id?: string;
          name?: string;
          description?: string | null;
          category?: string | null;
          price_cents?: number;
          cost_cents?: number;
          status?: ProductStatus;
          inventory?: number;
          sales_count?: number;
          metadata?: Json;
          created_at?: string;
          updated_at?: string;
        };
        Relationships: [
          {
            foreignKeyName: "products_business_id_fkey";
            columns: ["business_id"];
            isOneToOne: false;
            referencedRelation: "businesses";
            referencedColumns: ["id"];
          },
        ];
      };
      campaigns: {
        Row: {
          id: string;
          business_id: string;
          product_id: string | null;
          name: string;
          channel: CampaignChannel;
          status: CampaignStatus;
          budget_cents: number;
          spent_cents: number;
          impressions: number;
          clicks: number;
          conversions: number;
          start_date: string | null;
          end_date: string | null;
          metadata: Json;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          business_id: string;
          product_id?: string | null;
          name: string;
          channel: CampaignChannel;
          status?: CampaignStatus;
          budget_cents?: number;
          spent_cents?: number;
          impressions?: number;
          clicks?: number;
          conversions?: number;
          start_date?: string | null;
          end_date?: string | null;
          metadata?: Json;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          business_id?: string;
          product_id?: string | null;
          name?: string;
          channel?: CampaignChannel;
          status?: CampaignStatus;
          budget_cents?: number;
          spent_cents?: number;
          impressions?: number;
          clicks?: number;
          conversions?: number;
          start_date?: string | null;
          end_date?: string | null;
          metadata?: Json;
          created_at?: string;
          updated_at?: string;
        };
        Relationships: [
          {
            foreignKeyName: "campaigns_business_id_fkey";
            columns: ["business_id"];
            isOneToOne: false;
            referencedRelation: "businesses";
            referencedColumns: ["id"];
          },
          {
            foreignKeyName: "campaigns_product_id_fkey";
            columns: ["product_id"];
            isOneToOne: false;
            referencedRelation: "products";
            referencedColumns: ["id"];
          },
        ];
      };
      tasks: {
        Row: {
          id: string;
          business_id: string;
          title: string;
          description: string | null;
          status: TaskStatus;
          priority: TaskPriority;
          assigned_agent: string | null;
          payload: Json;
          result: Json | null;
          created_at: string;
          updated_at: string;
          completed_at: string | null;
        };
        Insert: {
          id?: string;
          business_id: string;
          title: string;
          description?: string | null;
          status?: TaskStatus;
          priority?: TaskPriority;
          assigned_agent?: string | null;
          payload?: Json;
          result?: Json | null;
          created_at?: string;
          updated_at?: string;
          completed_at?: string | null;
        };
        Update: {
          id?: string;
          business_id?: string;
          title?: string;
          description?: string | null;
          status?: TaskStatus;
          priority?: TaskPriority;
          assigned_agent?: string | null;
          payload?: Json;
          result?: Json | null;
          created_at?: string;
          updated_at?: string;
          completed_at?: string | null;
        };
        Relationships: [
          {
            foreignKeyName: "tasks_business_id_fkey";
            columns: ["business_id"];
            isOneToOne: false;
            referencedRelation: "businesses";
            referencedColumns: ["id"];
          },
        ];
      };
      agent_runs: {
        Row: {
          id: string;
          task_id: string | null;
          business_id: string;
          agent_name: string;
          agent_type: AgentType;
          status: AgentRunStatus;
          duration_ms: number | null;
          tokens_used: number;
          cost_cents: number;
          input_payload: Json;
          output_payload: Json | null;
          error_message: string | null;
          started_at: string;
          completed_at: string | null;
        };
        Insert: {
          id?: string;
          task_id?: string | null;
          business_id: string;
          agent_name: string;
          agent_type: AgentType;
          status?: AgentRunStatus;
          duration_ms?: number | null;
          tokens_used?: number;
          cost_cents?: number;
          input_payload?: Json;
          output_payload?: Json | null;
          error_message?: string | null;
          started_at?: string;
          completed_at?: string | null;
        };
        Update: {
          id?: string;
          task_id?: string | null;
          business_id?: string;
          agent_name?: string;
          agent_type?: AgentType;
          status?: AgentRunStatus;
          duration_ms?: number | null;
          tokens_used?: number;
          cost_cents?: number;
          input_payload?: Json;
          output_payload?: Json | null;
          error_message?: string | null;
          started_at?: string;
          completed_at?: string | null;
        };
        Relationships: [
          {
            foreignKeyName: "agent_runs_business_id_fkey";
            columns: ["business_id"];
            isOneToOne: false;
            referencedRelation: "businesses";
            referencedColumns: ["id"];
          },
          {
            foreignKeyName: "agent_runs_task_id_fkey";
            columns: ["task_id"];
            isOneToOne: false;
            referencedRelation: "tasks";
            referencedColumns: ["id"];
          },
        ];
      };
      approvals: {
        Row: {
          id: string;
          business_id: string;
          type: ApprovalType;
          title: string;
          description: string | null;
          status: ApprovalStatus;
          requested_by: string;
          reviewed_by: string | null;
          amount_cents: number | null;
          payload: Json;
          created_at: string;
          reviewed_at: string | null;
        };
        Insert: {
          id?: string;
          business_id: string;
          type: ApprovalType;
          title: string;
          description?: string | null;
          status?: ApprovalStatus;
          requested_by: string;
          reviewed_by?: string | null;
          amount_cents?: number | null;
          payload?: Json;
          created_at?: string;
          reviewed_at?: string | null;
        };
        Update: {
          id?: string;
          business_id?: string;
          type?: ApprovalType;
          title?: string;
          description?: string | null;
          status?: ApprovalStatus;
          requested_by?: string;
          reviewed_by?: string | null;
          amount_cents?: number | null;
          payload?: Json;
          created_at?: string;
          reviewed_at?: string | null;
        };
        Relationships: [
          {
            foreignKeyName: "approvals_business_id_fkey";
            columns: ["business_id"];
            isOneToOne: false;
            referencedRelation: "businesses";
            referencedColumns: ["id"];
          },
        ];
      };
      audit_logs: {
        Row: {
          id: string;
          business_id: string | null;
          actor: string;
          action: string;
          entity_type: string;
          entity_id: string | null;
          diff: Json | null;
          metadata: Json;
          created_at: string;
        };
        Insert: {
          id?: string;
          business_id?: string | null;
          actor: string;
          action: string;
          entity_type: string;
          entity_id?: string | null;
          diff?: Json | null;
          metadata?: Json;
          created_at?: string;
        };
        Update: never;
        Relationships: [
          {
            foreignKeyName: "audit_logs_business_id_fkey";
            columns: ["business_id"];
            isOneToOne: false;
            referencedRelation: "businesses";
            referencedColumns: ["id"];
          },
        ];
      };
      memory: {
        Row: {
          id: string;
          business_id: string | null;
          agent_name: string;
          namespace: string;
          key: string;
          value: Json;
          expires_at: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          business_id?: string | null;
          agent_name: string;
          namespace?: string;
          key: string;
          value: Json;
          expires_at?: string | null;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          business_id?: string | null;
          agent_name?: string;
          namespace?: string;
          key?: string;
          value?: Json;
          expires_at?: string | null;
          created_at?: string;
          updated_at?: string;
        };
        Relationships: [
          {
            foreignKeyName: "memory_business_id_fkey";
            columns: ["business_id"];
            isOneToOne: false;
            referencedRelation: "businesses";
            referencedColumns: ["id"];
          },
        ];
      };
      workflow_runs: {
        Row: {
          id: string;
          business_id: string;
          workflow_type: string;
          name: string;
          status: string;
          input_payload: Json;
          output_payload: Json | null;
          current_step: string | null;
          total_steps: number;
          completed_steps: number;
          failed_steps: number;
          total_tokens: number;
          total_cost_cents: number;
          error_message: string | null;
          created_at: string;
          updated_at: string;
          completed_at: string | null;
        };
        Insert: {
          id?: string;
          business_id: string;
          workflow_type: string;
          name: string;
          status?: string;
          input_payload?: Json;
          output_payload?: Json | null;
          current_step?: string | null;
          total_steps?: number;
          completed_steps?: number;
          failed_steps?: number;
          total_tokens?: number;
          total_cost_cents?: number;
          error_message?: string | null;
          created_at?: string;
          updated_at?: string;
          completed_at?: string | null;
        };
        Update: {
          id?: string;
          business_id?: string;
          workflow_type?: string;
          name?: string;
          status?: string;
          input_payload?: Json;
          output_payload?: Json | null;
          current_step?: string | null;
          total_steps?: number;
          completed_steps?: number;
          failed_steps?: number;
          total_tokens?: number;
          total_cost_cents?: number;
          error_message?: string | null;
          created_at?: string;
          updated_at?: string;
          completed_at?: string | null;
        };
        Relationships: [
          {
            foreignKeyName: "workflow_runs_business_id_fkey";
            columns: ["business_id"];
            isOneToOne: false;
            referencedRelation: "businesses";
            referencedColumns: ["id"];
          },
        ];
      };
      workflow_step_runs: {
        Row: {
          id: string;
          workflow_run_id: string;
          step_key: string;
          step_name: string;
          status: string;
          agent_name: string | null;
          input_payload: Json;
          output_payload: Json | null;
          error_message: string | null;
          approval_id: string | null;
          tokens_used: number;
          cost_cents: number;
          duration_ms: number;
          created_at: string;
          updated_at: string;
          started_at: string | null;
          completed_at: string | null;
        };
        Insert: {
          id?: string;
          workflow_run_id: string;
          step_key: string;
          step_name: string;
          status?: string;
          agent_name?: string | null;
          input_payload?: Json;
          output_payload?: Json | null;
          error_message?: string | null;
          approval_id?: string | null;
          tokens_used?: number;
          cost_cents?: number;
          duration_ms?: number;
          created_at?: string;
          updated_at?: string;
          started_at?: string | null;
          completed_at?: string | null;
        };
        Update: {
          id?: string;
          workflow_run_id?: string;
          step_key?: string;
          step_name?: string;
          status?: string;
          agent_name?: string | null;
          input_payload?: Json;
          output_payload?: Json | null;
          error_message?: string | null;
          approval_id?: string | null;
          tokens_used?: number;
          cost_cents?: number;
          duration_ms?: number;
          created_at?: string;
          updated_at?: string;
          started_at?: string | null;
          completed_at?: string | null;
        };
        Relationships: [
          {
            foreignKeyName: "workflow_step_runs_workflow_run_id_fkey";
            columns: ["workflow_run_id"];
            isOneToOne: false;
            referencedRelation: "workflow_runs";
            referencedColumns: ["id"];
          },
        ];
      };
      user_roles: {
        Row: {
          id: string;
          user_id: string;
          role: string;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          role?: string;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          role?: string;
          created_at?: string;
          updated_at?: string;
        };
        Relationships: [];
      };
    };
    Views: Record<string, never>;
    Functions: Record<string, never>;
    Enums: Record<string, never>;
    CompositeTypes: Record<string, never>;
  };
}

// ── Convenience type aliases ────────────────────────────────

export type BusinessRow = Database["public"]["Tables"]["businesses"]["Row"];
export type BusinessInsert = Database["public"]["Tables"]["businesses"]["Insert"];
export type BusinessUpdate = Database["public"]["Tables"]["businesses"]["Update"];

export type ProductRow = Database["public"]["Tables"]["products"]["Row"];
export type ProductInsert = Database["public"]["Tables"]["products"]["Insert"];
export type ProductUpdate = Database["public"]["Tables"]["products"]["Update"];

export type CampaignRow = Database["public"]["Tables"]["campaigns"]["Row"];
export type CampaignInsert = Database["public"]["Tables"]["campaigns"]["Insert"];
export type CampaignUpdate = Database["public"]["Tables"]["campaigns"]["Update"];

export type TaskRow = Database["public"]["Tables"]["tasks"]["Row"];
export type TaskInsert = Database["public"]["Tables"]["tasks"]["Insert"];
export type TaskUpdate = Database["public"]["Tables"]["tasks"]["Update"];

export type AgentRunRow = Database["public"]["Tables"]["agent_runs"]["Row"];
export type AgentRunInsert = Database["public"]["Tables"]["agent_runs"]["Insert"];
export type AgentRunUpdate = Database["public"]["Tables"]["agent_runs"]["Update"];

export type ApprovalRow = Database["public"]["Tables"]["approvals"]["Row"];
export type ApprovalInsert = Database["public"]["Tables"]["approvals"]["Insert"];
export type ApprovalUpdate = Database["public"]["Tables"]["approvals"]["Update"];

export type AuditLogRow = Database["public"]["Tables"]["audit_logs"]["Row"];
export type AuditLogInsert = Database["public"]["Tables"]["audit_logs"]["Insert"];

export type MemoryRow = Database["public"]["Tables"]["memory"]["Row"];
export type MemoryInsert = Database["public"]["Tables"]["memory"]["Insert"];
export type MemoryUpdate = Database["public"]["Tables"]["memory"]["Update"];
