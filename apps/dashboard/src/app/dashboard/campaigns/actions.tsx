"use client";

import { useState } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CreateCampaignForm } from "@/components/forms/create-campaign-form";
import type { BusinessRow } from "@abf/db";

export function CampaignPageActions({ businesses }: { businesses: BusinessRow[] }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button onClick={() => setOpen(true)}>
        <Plus className="mr-2 h-4 w-4" />
        New Campaign
      </Button>
      <CreateCampaignForm open={open} onClose={() => setOpen(false)} businesses={businesses} />
    </>
  );
}
