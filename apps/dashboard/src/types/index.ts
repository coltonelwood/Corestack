export interface Business {
  id: string;
  name: string;
  domain: string;
  status: "active" | "paused" | "setup";
  revenue: number;
  spend: number;
  productsCount: number;
  campaignsCount: number;
  createdAt: string;
}

export interface Product {
  id: string;
  businessId: string;
  businessName: string;
  name: string;
  category: string;
  price: number;
  status: "active" | "draft" | "archived";
  inventory: number;
  sales: number;
  createdAt: string;
}

export interface Campaign {
  id: string;
  businessId: string;
  businessName: string;
  name: string;
  channel: "google" | "meta" | "tiktok" | "email" | "linkedin";
  status: "active" | "paused" | "completed" | "draft";
  budget: number;
  spent: number;
  impressions: number;
  clicks: number;
  conversions: number;
  startDate: string;
  endDate: string;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  status: "pending" | "in_progress" | "completed" | "failed";
  priority: "low" | "medium" | "high" | "critical";
  assignedAgent: string;
  businessName: string;
  createdAt: string;
  completedAt: string | null;
}

export interface AgentRun {
  id: string;
  agentName: string;
  agentType: "research" | "content" | "ads" | "analytics" | "outreach" | "operations";
  status: "running" | "completed" | "failed" | "queued";
  taskDescription: string;
  businessName: string;
  duration: number | null;
  tokensUsed: number;
  startedAt: string;
  completedAt: string | null;
}

export interface Approval {
  id: string;
  type: "campaign_launch" | "budget_increase" | "content_publish" | "product_listing" | "price_change";
  title: string;
  description: string;
  status: "pending" | "approved" | "rejected";
  requestedBy: string;
  businessName: string;
  amount: number | null;
  createdAt: string;
  reviewedAt: string | null;
}

export interface ActivityItem {
  id: string;
  agent: string;
  action: string;
  target: string;
  timestamp: string;
}

export interface MetricCard {
  title: string;
  value: string;
  change: string;
  changeType: "positive" | "negative" | "neutral";
  icon: string;
}
