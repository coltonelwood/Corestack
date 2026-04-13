"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Building2,
  Package,
  Megaphone,
  ListTodo,
  Bot,
  ShieldCheck,
  Settings,
  Menu,
  X,
  Zap,
} from "lucide-react";

const navigation = [
  { name: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { name: "Businesses", href: "/dashboard/businesses", icon: Building2 },
  { name: "Products", href: "/dashboard/products", icon: Package },
  { name: "Campaigns", href: "/dashboard/campaigns", icon: Megaphone },
  { name: "Tasks", href: "/dashboard/tasks", icon: ListTodo },
  { name: "Agent Runs", href: "/dashboard/agent-runs", icon: Bot },
  { name: "Approvals", href: "/dashboard/approvals", icon: ShieldCheck },
  { name: "Settings", href: "/dashboard/settings", icon: Settings },
];

export function MobileSidebar() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="lg:hidden p-2 text-muted-foreground hover:text-foreground"
        aria-label="Open menu"
      >
        <Menu className="h-5 w-5" />
      </button>

      {open && (
        <>
          <div
            className="fixed inset-0 z-40 bg-black/50 lg:hidden"
            onClick={() => setOpen(false)}
          />
          <div className="fixed inset-y-0 left-0 z-50 w-64 bg-card shadow-xl lg:hidden">
            <div className="flex h-16 items-center justify-between border-b px-6">
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
                  <Zap className="h-4 w-4 text-primary-foreground" />
                </div>
                <span className="text-lg font-bold tracking-tight">ABF</span>
              </div>
              <button
                onClick={() => setOpen(false)}
                className="p-1 text-muted-foreground hover:text-foreground"
                aria-label="Close menu"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <nav className="flex flex-col gap-1 p-4">
              {navigation.map((item) => {
                const isActive =
                  pathname === item.href ||
                  (item.href !== "/dashboard" &&
                    pathname.startsWith(item.href));
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setOpen(false)}
                    className={cn(
                      "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
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
            </nav>
          </div>
        </>
      )}
    </>
  );
}
