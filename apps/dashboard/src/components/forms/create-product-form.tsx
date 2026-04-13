"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Dialog } from "@/components/ui/dialog";
import { createProduct } from "@/app/actions/products";
import { Loader2 } from "lucide-react";
import type { BusinessRow } from "@abf/db";

interface CreateProductFormProps {
  open: boolean;
  onClose: () => void;
  businesses: BusinessRow[];
}

export function CreateProductForm({
  open,
  onClose,
  businesses,
}: CreateProductFormProps) {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setPending(true);
    setError(null);

    const formData = new FormData(e.currentTarget);
    const result = await createProduct(formData);

    setPending(false);

    if (result.error) {
      setError(result.error);
      return;
    }

    onClose();
    router.refresh();
  }

  return (
    <Dialog open={open} onClose={onClose} title="Add Product" description="Create a new product for one of your businesses.">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <label htmlFor="prod-biz" className="text-sm font-medium">Business</label>
          <Select id="prod-biz" name="business_id" required>
            <option value="">Select a business...</option>
            {businesses.map((b) => (
              <option key={b.id} value={b.id}>{b.name}</option>
            ))}
          </Select>
        </div>
        <div className="space-y-2">
          <label htmlFor="prod-name" className="text-sm font-medium">Product Name</label>
          <Input id="prod-name" name="name" placeholder="e.g. Vitamin C Serum" required />
        </div>
        <div className="space-y-2">
          <label htmlFor="prod-desc" className="text-sm font-medium">Description</label>
          <Textarea id="prod-desc" name="description" placeholder="Product description..." rows={2} />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <label htmlFor="prod-cat" className="text-sm font-medium">Category</label>
            <Input id="prod-cat" name="category" placeholder="e.g. Serums" />
          </div>
          <div className="space-y-2">
            <label htmlFor="prod-inv" className="text-sm font-medium">Inventory</label>
            <Input id="prod-inv" name="inventory" type="number" min="0" defaultValue="0" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <label htmlFor="prod-price" className="text-sm font-medium">Price ($)</label>
            <Input id="prod-price" name="price" type="number" step="0.01" min="0" required placeholder="42.00" />
          </div>
          <div className="space-y-2">
            <label htmlFor="prod-cost" className="text-sm font-medium">Cost ($)</label>
            <Input id="prod-cost" name="cost" type="number" step="0.01" min="0" defaultValue="0" placeholder="8.40" />
          </div>
        </div>
        {error && <p className="text-sm text-destructive">{error}</p>}
        <div className="flex justify-end gap-2 pt-2">
          <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
          <Button type="submit" disabled={pending}>
            {pending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Add Product
          </Button>
        </div>
      </form>
    </Dialog>
  );
}
