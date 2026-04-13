"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Dialog } from "@/components/ui/dialog";
import { createBusiness } from "@/app/actions/businesses";
import { Loader2 } from "lucide-react";

interface CreateBusinessFormProps {
  open: boolean;
  onClose: () => void;
}

export function CreateBusinessForm({ open, onClose }: CreateBusinessFormProps) {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setPending(true);
    setError(null);

    const formData = new FormData(e.currentTarget);
    const result = await createBusiness(formData);

    setPending(false);

    if (result.error) {
      setError(result.error);
      return;
    }

    onClose();
    router.refresh();
  }

  return (
    <Dialog open={open} onClose={onClose} title="Create Business" description="Add a new autonomous business to your portfolio.">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <label htmlFor="biz-name" className="text-sm font-medium">Name</label>
          <Input id="biz-name" name="name" placeholder="e.g. NovaBright Skincare" required />
        </div>
        <div className="space-y-2">
          <label htmlFor="biz-domain" className="text-sm font-medium">Domain</label>
          <Input id="biz-domain" name="domain" placeholder="e.g. novabrightskin.com" />
        </div>
        <div className="space-y-2">
          <label htmlFor="biz-desc" className="text-sm font-medium">Description</label>
          <Textarea id="biz-desc" name="description" placeholder="Brief description of the business..." rows={3} />
        </div>
        {error && <p className="text-sm text-destructive">{error}</p>}
        <div className="flex justify-end gap-2 pt-2">
          <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
          <Button type="submit" disabled={pending}>
            {pending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Create Business
          </Button>
        </div>
      </form>
    </Dialog>
  );
}
