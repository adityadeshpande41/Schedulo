import { motion } from "framer-motion";
import { Link } from "wouter";
import { Button } from "@/components/ui/button";
import { ScheduloAssistant } from "@/components/schedulo/assistant";
import { ShinyText } from "@/components/schedulo/shiny-text";
import { usePageMeta } from "@/hooks/use-page-meta";
import { agentInfoList } from "@/data/mock";
import {
  ArrowRight,
  Sparkles,
  CalendarSearch,
  Brain,
  Users,
  Cpu,
  Shield,
  Zap,
  Eye,
  ChevronRight,
} from "lucide-react";

const fadeUp = {
  initial: { opacity: 0, y: 30 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-50px" },
  transition: { duration: 0.6 },
};

const stagger = {
  initial: { opacity: 0, y: 20 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true },
};

const capabilities = [
  { icon: CalendarSearch, title: "Availability Detection", desc: "Scans all calendars in real-time across timezones" },
  { icon: Brain, title: "Preference-Aware", desc: "Learns your scheduling style and optimizes over time" },
  { icon: Users, title: "Multi-Agent Coordination", desc: "Intelligent negotiation across all attendees" },
  { icon: Eye, title: "Explainable Ranking", desc: "Transparent reasoning for every recommendation" },
  { icon: Shield, title: "Human Escalation", desc: "Hands off to you when confidence is low" },
  { icon: Zap, title: "Instant Scheduling", desc: "Finds the best slot in seconds, not minutes" },
];

const agentIcons: Record<string, typeof Cpu> = {
  calendar: CalendarSearch,
  behavior: Brain,
  coordination: Users,
  orchestrator: Cpu,
};

export default function Landing() {
  usePageMeta({ title: "Schedulo — AI-Powered Multi-Agent Scheduling", description: "Schedulo orchestrates multiple AI agents to find the perfect meeting time." });

  return (
    <div className="min-h-screen bg-background">
      <section className="relative pt-32 pb-24 px-4 sm:px-6 overflow-hidden">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[800px] rounded-full bg-primary/5 blur-3xl" />
          <div className="absolute top-1/3 left-1/4 w-[400px] h-[400px] rounded-full bg-purple-500/5 blur-3xl" />
        </div>

        <div className="max-w-5xl mx-auto text-center relative z-10">
          <motion.div {...fadeUp} className="mb-8">
            <ScheduloAssistant size="xl" glowing className="mx-auto mb-8" />
          </motion.div>

          <motion.div {...fadeUp} transition={{ duration: 0.6, delay: 0.15 }}>
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-primary/20 bg-primary/5 text-primary text-sm font-medium mb-6">
              <Sparkles className="h-3.5 w-3.5" />
              AI-Powered Multi-Agent Scheduling
            </div>
          </motion.div>

          <motion.div {...fadeUp} transition={{ duration: 0.6, delay: 0.25 }}>
            <ShinyText
              as="h1"
              className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight leading-[1.1] mb-6"
            >
              Scheduling, Reinvented by AI Agents
            </ShinyText>
          </motion.div>

          <motion.p
            {...fadeUp}
            transition={{ duration: 0.6, delay: 0.35 }}
            className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed"
          >
            Schedulo orchestrates multiple AI agents to find the perfect meeting time — analyzing calendars, learning preferences, and negotiating across attendees automatically.
          </motion.p>

          <motion.div
            {...fadeUp}
            transition={{ duration: 0.6, delay: 0.45 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Link href="/dashboard">
              <Button size="lg" className="gap-2 text-base px-8" data-testid="button-try-demo">
                Try Demo
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/agents">
              <Button variant="outline" size="lg" className="gap-2 text-base px-8" data-testid="button-view-agents">
                View Agent Flow
                <ChevronRight className="h-4 w-4" />
              </Button>
            </Link>
          </motion.div>
        </div>
      </section>

      <section className="py-24 px-4 sm:px-6 border-t border-border/50">
        <div className="max-w-6xl mx-auto">
          <motion.div {...fadeUp} className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
              How Schedulo Works
            </h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              Four specialized AI agents collaborate to deliver optimal scheduling decisions in seconds.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-4 gap-6">
            {agentInfoList.map((agent, i) => {
              const Icon = agentIcons[agent.type];
              return (
                <motion.div
                  key={agent.type}
                  {...stagger}
                  transition={{ duration: 0.5, delay: i * 0.1 }}
                  className="group relative"
                >
                  <div className="relative rounded-xl border border-border/60 bg-card p-6 h-full transition-all duration-300 hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5">
                    <div className="flex items-center gap-3 mb-4">
                      <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${agent.color} flex items-center justify-center`}>
                        <Icon className="h-5 w-5 text-white" />
                      </div>
                      <div className="text-xs font-mono text-muted-foreground uppercase tracking-wider">
                        Step {i + 1}
                      </div>
                    </div>
                    <h3 className="text-base font-semibold mb-2">{agent.name}</h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">{agent.description}</p>
                    {i < 3 && (
                      <div className="hidden md:block absolute -right-3 top-1/2 -translate-y-1/2 z-10">
                        <ChevronRight className="h-5 w-5 text-muted-foreground/40" />
                      </div>
                    )}
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="py-24 px-4 sm:px-6 bg-card/50">
        <div className="max-w-6xl mx-auto">
          <motion.div {...fadeUp} className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
              Intelligent Capabilities
            </h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              Every feature is designed to save time and reduce scheduling friction.
            </p>
          </motion.div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {capabilities.map((cap, i) => (
              <motion.div
                key={cap.title}
                {...stagger}
                transition={{ duration: 0.5, delay: i * 0.08 }}
                className="group rounded-xl border border-border/60 bg-card p-6 transition-all duration-300 hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5"
              >
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                  <cap.icon className="h-5 w-5 text-primary" />
                </div>
                <h3 className="text-base font-semibold mb-2">{cap.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{cap.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-24 px-4 sm:px-6 border-t border-border/50">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div {...fadeUp}>
            <ScheduloAssistant size="lg" glowing className="mx-auto mb-8" />
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
              Ready to Transform Your Scheduling?
            </h2>
            <p className="text-muted-foreground text-lg max-w-xl mx-auto mb-8">
              Experience the future of intelligent meeting coordination.
            </p>
            <Link href="/dashboard">
              <Button size="lg" className="gap-2 text-base px-10" data-testid="button-cta-bottom">
                Try the Demo
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </motion.div>
        </div>
      </section>

      <footer className="border-t border-border/50 py-12 px-4 sm:px-6">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <ScheduloAssistant size="sm" animate={false} />
            <span className="text-sm font-semibold bg-clip-text text-transparent bg-gradient-to-r from-primary to-purple-500">
              Schedulo
            </span>
          </div>
          <p className="text-xs text-muted-foreground">
            AI-powered multi-agent scheduling platform. Frontend demo.
          </p>
        </div>
      </footer>
    </div>
  );
}
