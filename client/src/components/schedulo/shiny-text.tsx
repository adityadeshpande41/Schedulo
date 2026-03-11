import { cn } from "@/lib/utils";

interface ShinyTextProps {
  children: string;
  className?: string;
  as?: "h1" | "h2" | "h3" | "span" | "p";
}

export function ShinyText({ children, className, as: Tag = "h1" }: ShinyTextProps) {
  return (
    <Tag
      className={cn(
        "bg-clip-text text-transparent bg-[length:200%_auto] animate-[shimmer_3s_linear_infinite]",
        "bg-gradient-to-r from-foreground via-primary to-foreground dark:from-white dark:via-blue-400 dark:to-white",
        className
      )}
      style={{
        backgroundSize: "200% auto",
      }}
    >
      {children}
    </Tag>
  );
}
