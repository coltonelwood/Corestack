"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { canAccessRoute, type Role, ROLE_LABELS, hasPermission } from "@/lib/rbac";
import {
  LayoutDashboard,
  Building2,
  Package,
  Megaphone,
  ListTodo,
  Bot,
  ShieldCheck,
  Settings,
  Zap,
  Workflow,
} from "lucide-react";

const mainNav = [
  { name: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { name: "Businesses", href: "/dashboard/businesses", icon: Building2 },
  { name: "Products", href: "/dashboard/products", icon: Package },
  { name: "Campaigns", href: "/dashboard/campaigns", icon: Megaphone },
];

const automationNav = [
  { name: "Tasks", href: "/dashboard/tasks", icon: ListTodo },
  { name: "Agent Runs", href: "/dashboard/agent-runs", icon: Bot },
  { name: "Workflows", href: "/dashboard/workflows", icon: Workflow },
  { name: "Approvals", href: "/dashboard/approvals", icon: ShieldCheck },
];

const systemNav = [
  { name: "Integrations", href: "/dashboard/integrations", icon: Zap },
  { name: "Settings", href: "/dashboard/settings", icon: Settings },
];

function NavGroup({
  label,
  items,
  pathname,
  role,
}: {
  label?: string;
  items: typeof mainNav;
  pathname: string;
  role: Role;
}) {
  const visible = items.filter((item) => canAccessRoute(role, item.href));
  if (visible.length === 0) return null;

  return (
    <div>
      {label && (
        <p className="mb-1 px-3 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/60">
          {label}
        </p>
      )}
      <div className="flex flex-col gap-0.5">
        {visible.map((item) => {
          const isActive =
            pathname === item.href ||
            (item.href !== "/dashboard" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-[13px] font-medium transition-colors",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.name}
            </Link>
          );
        })}
      </div>
    </div>
  );
}

export function Sidebar({ role }: { role: Role }) {
  const pathname = usePathname();

  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-60 border-r bg-card lg:block">
      <div className="flex h-14 items-center gap-2.5 border-b px-5">
        <div className="flex h-7 w-7 items-center justify-center rounded-md bg-primary">
          <Zap className="h-3.5 w-3.5 text-primary-foreground" />
        </div>
        <span className="text-sm font-bold tracking-tight">ABF</span>
      </div>
      <nav className="flex flex-col gap-6 p-3 pt-4">
        <NavGroup items={mainNav} pathname={pathname} role={role} />
        <NavGroup label="Automation" items={automationNav} pathname={pathname} role={role} />
        <NavGroup label="System" items={systemNav} pathname={pathname} role={role} />
      </nav>
      <div className="absolute bottom-0 left-0 right-0 border-t px-5 py-3">
        <p className="text-[10px] font-medium uppercase tracking-widest text-muted-foreground/60">
          {ROLE_LABELS[role]}
        </p>
      </div>
    </aside>
  );
}
