"use client";

import { Bell, Search } from "lucide-react";
import { Avatar } from "@/components/ui/avatar";
import { MobileSidebar } from "./mobile-sidebar";

export function Header() {
  return (
    <header className="sticky top-0 z-20 flex h-16 items-center gap-4 border-b bg-card px-4 lg:px-6">
      <MobileSidebar />

      <div className="relative flex-1 max-w-md">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search businesses, tasks, agents..."
          className="h-9 w-full rounded-md border border-input bg-background pl-9 pr-3 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        />
      </div>

      <div className="flex items-center gap-3 ml-auto">
        <button className="relative p-2 text-muted-foreground hover:text-foreground transition-colors">
          <Bell className="h-5 w-5" />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-destructive" />
        </button>
        <div className="hidden sm:flex items-center gap-2">
          <Avatar fallback="CE" size="sm" />
          <div className="text-sm">
            <p className="font-medium leading-none">Colton E.</p>
            <p className="text-xs text-muted-foreground mt-0.5">Admin</p>
          </div>
        </div>
      </div>
    </header>
  );
}
