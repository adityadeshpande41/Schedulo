import { Link, useLocation } from "wouter";
import { motion } from "framer-motion";
import { ScheduloAssistant } from "./assistant";
import { ThemeToggle } from "./theme-toggle";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { LayoutDashboard, Workflow, Sparkles } from "lucide-react";

interface NavbarProps {
  theme: "light" | "dark";
  onToggleTheme: () => void;
  variant?: "landing" | "app";
}

const appLinks = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/agents", label: "Agent Flow", icon: Workflow },
  { href: "/decision", label: "AI Cockpit", icon: Sparkles },
];

export function Navbar({ theme, onToggleTheme, variant = "landing" }: NavbarProps) {
  const [location] = useLocation();

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.4 }}
      className={cn(
        "fixed top-0 left-0 right-0 z-50 border-b",
        "backdrop-blur-xl bg-background/80",
        "border-border/50"
      )}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        <Link href={variant === "landing" ? "/" : "/dashboard"}>
          <div className="flex items-center gap-2.5 cursor-pointer group" data-testid="link-home">
            <ScheduloAssistant size="sm" animate={false} />
            <span className="text-lg font-semibold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary to-purple-500">
              Schedulo
            </span>
          </div>
        </Link>

        <nav className="hidden md:flex items-center gap-1">
          {variant === "app" &&
            appLinks.map((link) => {
              const active = location === link.href;
              return (
                <Link key={link.href} href={link.href}>
                  <Button
                    variant={active ? "secondary" : "ghost"}
                    size="sm"
                    className={cn(
                      "gap-2 text-sm font-medium relative",
                      active && "text-primary"
                    )}
                    data-testid={`link-${link.label.toLowerCase().replace(/\s/g, "-")}`}
                  >
                    <link.icon className="h-4 w-4" />
                    {link.label}
                    {active && (
                      <motion.div
                        layoutId="nav-indicator"
                        className="absolute -bottom-[1.0625rem] left-0 right-0 h-0.5 bg-primary rounded-full"
                        transition={{ type: "spring", stiffness: 500, damping: 30 }}
                      />
                    )}
                  </Button>
                </Link>
              );
            })}
          {variant === "landing" && (
            <>
              <Link href="/dashboard">
                <Button variant="ghost" size="sm" data-testid="link-try-demo">Try Demo</Button>
              </Link>
              <Link href="/agents">
                <Button variant="ghost" size="sm" data-testid="link-agent-flow">Agent Flow</Button>
              </Link>
            </>
          )}
        </nav>

        <div className="flex items-center gap-2">
          <ThemeToggle theme={theme} onToggle={onToggleTheme} />
          {variant === "app" && (
            <Avatar className="h-8 w-8 border border-border" data-testid="img-avatar">
              <AvatarFallback className="text-xs font-medium bg-primary/10 text-primary">AR</AvatarFallback>
            </Avatar>
          )}
          {variant === "landing" && (
            <Link href="/dashboard">
              <Button size="sm" className="gap-1.5" data-testid="button-get-started">
                <Sparkles className="h-3.5 w-3.5" />
                Get Started
              </Button>
            </Link>
          )}
        </div>
      </div>
    </motion.header>
  );
}
