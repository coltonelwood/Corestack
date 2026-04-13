"use client";

import { useState } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CreateProductForm } from "@/components/forms/create-product-form";
import type { BusinessRow } from "@abf/db";

export function ProductPageActions({ businesses }: { businesses: BusinessRow[] }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button onClick={() => setOpen(true)}>
        <Plus className="mr-2 h-4 w-4" />
        Add Product
      </Button>
      <CreateProductForm open={open} onClose={() => setOpen(false)} businesses={businesses} />
    </>
  );
}
