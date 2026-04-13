"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Dialog } from "@/components/ui/dialog";
import { createCampaign } from "@/app/actions/campaigns";
import { Loader2 } from "lucide-react";
import type { BusinessRow } from "@abf/db";

interface CreateCampaignFormProps {
  open: boolean;
  onClose: () => void;
  businesses: BusinessRow[];
}

export function CreateCampaignForm({
  open,
  onClose,
  businesses,
}: CreateCampaignFormProps) {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setPending(true);
    setError(null);

    const formData = new FormData(e.currentTarget);
    const result = await createCampaign(formData);

    setPending(false);

    if (result.error) {
      setError(result.error);
      return;
    }

    onClose();
    router.refresh();
  }

  return (
    <Dialog open={open} onClose={onClose} title="Create Campaign" description="Draft a new marketing campaign.">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <label htmlFor="camp-biz" className="text-sm font-medium">Business</label>
          <Select id="camp-biz" name="business_id" required>
            <option value="">Select a business...</option>
            {businesses.map((b) => (
              <option key={b.id} value={b.id}>{b.name}</option>
            ))}
          </Select>
        </div>
        <div className="space-y-2">
          <label htmlFor="camp-name" className="text-sm font-medium">Campaign Name</label>
          <Input id="camp-name" name="name" placeholder="e.g. Spring Launch Campaign" required />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <label htmlFor="camp-channel" className="text-sm font-medium">Channel</label>
            <Select id="camp-channel" name="channel" required>
              <option value="">Select channel...</option>
              <option value="google">Google Ads</option>
              <option value="meta">Meta</option>
              <option value="tiktok">TikTok</option>
              <option value="email">Email</option>
              <option value="linkedin">LinkedIn</option>
              <option value="other">Other</option>
            </Select>
          </div>
          <div className="space-y-2">
            <label htmlFor="camp-budget" className="text-sm font-medium">Budget ($)</label>
            <Input id="camp-budget" name="budget" type="number" step="0.01" min="0" required placeholder="10000" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <label htmlFor="camp-start" className="text-sm font-medium">Start Date</label>
            <Input id="camp-start" name="start_date" type="date" />
          </div>
          <div className="space-y-2">
            <label htmlFor="camp-end" className="text-sm font-medium">End Date</label>
            <Input id="camp-end" name="end_date" type="date" />
          </div>
        </div>
        {error && <p className="text-sm text-destructive">{error}</p>}
        <div className="flex justify-end gap-2 pt-2">
          <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
          <Button type="submit" disabled={pending}>
            {pending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Create Draft
          </Button>
        </div>
      </form>
    </Dialog>
  );
}
