"use client";

import { useState } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CreateBusinessForm } from "@/components/forms/create-business-form";

export function BusinessPageActions() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button onClick={() => setOpen(true)}>
        <Plus className="mr-2 h-4 w-4" />
        New Business
      </Button>
      <CreateBusinessForm open={open} onClose={() => setOpen(false)} />
    </>
  );
}
