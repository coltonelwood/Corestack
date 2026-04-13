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
          <tr className="border-b text-left">
            {columns.map((col) => (
              <th
                key={col.header}
                className={cn(
                  "whitespace-nowrap px-4 py-3 font-medium text-muted-foreground",
                  col.className
                )}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr
              key={row.id}
              className="border-b last:border-0 hover:bg-muted/50 transition-colors"
            >
              {columns.map((col) => (
                <td
                  key={col.header}
                  className={cn("whitespace-nowrap px-4 py-3", col.className)}
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
    </div>
  );
}
