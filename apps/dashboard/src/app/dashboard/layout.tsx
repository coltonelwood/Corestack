import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { getUserWithRole } from "@/app/actions/auth";
import type { Role } from "@/lib/rbac";

export const dynamic = "force-dynamic";

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const user = await getUserWithRole();
  const role: Role = user?.role ?? "viewer";

  return (
    <div className="min-h-screen">
      <Sidebar role={role} />
      <div className="lg:pl-60">
        <Header role={role} email={user?.email} />
        <main className="px-4 py-6 lg:px-8">{children}</main>
      </div>
    </div>
  );
}
