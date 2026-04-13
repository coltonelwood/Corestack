import { cn } from "@/lib/utils";

interface AvatarProps extends React.HTMLAttributes<HTMLDivElement> {
  fallback: string;
  size?: "sm" | "md" | "lg";
}

const sizeMap = {
  sm: "h-8 w-8 text-xs",
  md: "h-10 w-10 text-sm",
  lg: "h-12 w-12 text-base",
};

export function Avatar({
  fallback,
  size = "md",
  className,
  ...props
}: AvatarProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center justify-center rounded-full bg-primary/10 font-medium text-primary",
        sizeMap[size],
        className
      )}
      {...props}
    >
      {fallback}
    </div>
  );
}
