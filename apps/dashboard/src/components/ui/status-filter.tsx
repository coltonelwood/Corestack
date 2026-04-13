"use client";

import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

interface FilterOption {
  label: string;
  value: string;
  count?: number;
}

interface StatusFilterProps {
  options: FilterOption[];
  paramName?: string;
}

export function StatusFilter({ options, paramName = "status" }: StatusFilterProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const current = searchParams.get(paramName) ?? "";

  function handleClick(value: string) {
    const params = new URLSearchParams(searchParams.toString());
    if (value === current || value === "") {
      params.delete(paramName);
    } else {
      params.set(paramName, value);
    }
    const qs = params.toString();
    router.push(qs ? `${pathname}?${qs}` : pathname);
  }

  return (
    <div className="flex items-center gap-1 rounded-lg bg-muted/60 p-1">
      {options.map((opt) => (
        <button
          key={opt.value}
          onClick={() => handleClick(opt.value)}
          className={cn(
            "rounded-md px-3 py-1.5 text-xs font-medium transition-colors",
            (opt.value === current || (opt.value === "" && !current))
              ? "bg-card text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground"
          )}
        >
          {opt.label}
          {opt.count !== undefined && (
            <span className="ml-1.5 text-muted-foreground">{opt.count}</span>
          )}
        </button>
      ))}
    </div>
  );
}
