"use client";

import { Bell, LogOut, Search, ChevronDown, Building2 } from "lucide-react";
import { Avatar } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { MobileSidebar } from "./mobile-sidebar";
import { signOut } from "@/app/actions/auth";
import { ROLE_LABELS, type Role } from "@/lib/rbac";

export function Header({ role, email }: { role: Role; email?: string }) {
  return (
    <header className="sticky top-0 z-20 flex h-14 items-center gap-4 border-b bg-card/80 backdrop-blur-sm px-4 lg:px-6">
      <MobileSidebar />

      <button className="hidden md:flex items-center gap-2 rounded-lg border bg-background px-3 py-1.5 text-sm hover:bg-muted transition-colors">
        <Building2 className="h-3.5 w-3.5 text-muted-foreground" />
        <span className="font-medium">All Businesses</span>
        <ChevronDown className="h-3 w-3 text-muted-foreground" />
      </button>

      <div className="relative flex-1 max-w-sm">
        <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search..."
          className="h-8 w-full rounded-lg border border-input bg-background pl-8 pr-3 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        />
      </div>

      <div className="flex items-center gap-2 ml-auto">
        <button className="relative rounded-lg p-2 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors">
          <Bell className="h-4 w-4" />
          <span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-destructive" />
        </button>
        <div className="h-5 w-px bg-border" />
        <div className="hidden sm:flex items-center gap-2">
          <Avatar fallback={email ? email.charAt(0).toUpperCase() : "U"} size="sm" />
          <div className="hidden md:block">
            <p className="text-xs font-medium leading-none">{email ?? ""}</p>
            <p className="text-[10px] text-muted-foreground mt-0.5">{ROLE_LABELS[role]}</p>
          </div>
        </div>
        <button
          onClick={() => signOut()}
          className="rounded-lg p-2 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
          title="Sign out"
        >
          <LogOut className="h-4 w-4" />
        </button>
      </div>
    </header>
  );
}
