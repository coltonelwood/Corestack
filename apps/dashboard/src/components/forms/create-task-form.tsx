"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Dialog } from "@/components/ui/dialog";
import { createTask } from "@/app/actions/tasks";
import { Loader2 } from "lucide-react";
import type { BusinessRow } from "@abf/db";

interface CreateTaskFormProps {
  open: boolean;
  onClose: () => void;
  businesses: BusinessRow[];
}

export function CreateTaskForm({
  open,
  onClose,
  businesses,
}: CreateTaskFormProps) {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setPending(true);
    setError(null);

    const formData = new FormData(e.currentTarget);
    const result = await createTask(formData);

    setPending(false);

    if (result.error) {
      setError(result.error);
      return;
    }

    onClose();
    router.refresh();
  }

  return (
    <Dialog open={open} onClose={onClose} title="Create Task" description="Assign a new task to an AI agent.">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <label htmlFor="task-biz" className="text-sm font-medium">Business</label>
          <Select id="task-biz" name="business_id" required>
            <option value="">Select a business...</option>
            {businesses.map((b) => (
              <option key={b.id} value={b.id}>{b.name}</option>
            ))}
          </Select>
        </div>
        <div className="space-y-2">
          <label htmlFor="task-title" className="text-sm font-medium">Title</label>
          <Input id="task-title" name="title" placeholder="e.g. Generate product descriptions" required />
        </div>
        <div className="space-y-2">
          <label htmlFor="task-desc" className="text-sm font-medium">Description</label>
          <Textarea id="task-desc" name="description" placeholder="Detailed instructions for the agent..." rows={3} />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <label htmlFor="task-priority" className="text-sm font-medium">Priority</label>
            <Select id="task-priority" name="priority" defaultValue="medium">
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </Select>
          </div>
          <div className="space-y-2">
            <label htmlFor="task-agent" className="text-sm font-medium">Assign Agent</label>
            <Select id="task-agent" name="assigned_agent">
              <option value="">Unassigned</option>
              <option value="Content Writer">Content Writer</option>
              <option value="Ads Manager">Ads Manager</option>
              <option value="Research Analyst">Research Analyst</option>
              <option value="Analytics Agent">Analytics Agent</option>
              <option value="Operations Agent">Operations Agent</option>
              <option value="Outreach Agent">Outreach Agent</option>
            </Select>
          </div>
        </div>
        {error && <p className="text-sm text-destructive">{error}</p>}
        <div className="flex justify-end gap-2 pt-2">
          <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
          <Button type="submit" disabled={pending}>
            {pending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Create Task
          </Button>
        </div>
      </form>
    </Dialog>
  );
}
