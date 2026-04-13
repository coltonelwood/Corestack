"use client";

import { useState } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CreateTaskForm } from "@/components/forms/create-task-form";
import type { BusinessRow } from "@abf/db";

export function TaskPageActions({ businesses }: { businesses: BusinessRow[] }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button onClick={() => setOpen(true)}>
        <Plus className="mr-2 h-4 w-4" />
        Create Task
      </Button>
      <CreateTaskForm open={open} onClose={() => setOpen(false)} businesses={businesses} />
    </>
  );
}
