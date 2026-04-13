import { cn } from "@/lib/utils";

interface Column<T> {
  header: string;
  accessorKey?: keyof T;
  cell?: (row: T) => React.ReactNode;
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  className?: string;
}

export function DataTable<T extends { id: string }>({
  columns,
  data,
  className,
}: DataTableProps<T>) {
  return (
    <div className={cn("overflow-x-auto", className)}>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b bg-muted/40 text-left">
            {columns.map((col) => (
              <th
                key={col.header}
                className={cn(
                  "whitespace-nowrap px-4 py-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground",
                  col.className
                )}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y">
          {data.map((row) => (
            <tr
              key={row.id}
              className="hover:bg-muted/30 transition-colors"
            >
              {columns.map((col) => (
                <td
                  key={col.header}
                  className={cn("whitespace-nowrap px-4 py-3.5", col.className)}
                >
                  {col.cell
                    ? col.cell(row)
                    : col.accessorKey
                      ? String(row[col.accessorKey] ?? "")
                      : null}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {data.length > 0 && (
        <div className="border-t px-4 py-2.5 text-xs text-muted-foreground bg-muted/20">
          {data.length} {data.length === 1 ? "record" : "records"}
        </div>
      )}
    </div>
  );
}
