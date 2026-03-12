import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScheduloAssistant } from "@/components/schedulo/assistant";
import { usePageMeta } from "@/hooks/use-page-meta";
import { useAgentInfo } from "@/hooks/use-agents";
import { Link } from "wouter";
import {
  CalendarSearch,
  Brain,
  Users,
  Cpu,
  ArrowDown,
  ArrowRight,
  Lock,
  Unlock,
  Shield,
  Zap,
  Eye,
  CheckCircle2,
} from "lucide-react";
import { cn } from "@/lib/utils";

const agentIcons: Record<string, typeof Cpu> = {
  calendar: CalendarSearch,
  behavior: Brain,
  coordination: Users,
  orchestrator: Cpu,
};

const flowSteps = [
  {
    label: "Input",
    desc: "Meeting request with attendees, duration, and priority",
    icon: Zap,
    color: "from-blue-500/20 to-blue-500/5",
    border: "border-blue-500/30",
  },
  {
    label: "Private Intelligence",
    desc: "Each attendee's local agent processes private calendar and preference data",
    icon: Lock,
    color: "from-purple-500/20 to-purple-500/5",
    border: "border-purple-500/30",
  },
  {
    label: "Constrained Sharing",
    desc: "Only availability signals and preference constraints are shared — never raw data",
    icon: Unlock,
    color: "from-amber-500/20 to-amber-500/5",
    border: "border-amber-500/30",
  },
  {
    label: "Negotiation",
    desc: "Coordination agent negotiates across all attendee constraints to find consensus",
    icon: Users,
    color: "from-orange-500/20 to-orange-500/5",
    border: "border-orange-500/30",
  },
  {
    label: "Ranked Output",
    desc: "Orchestrator synthesizes signals into ranked, explainable recommendations",
    icon: Eye,
    color: "from-emerald-500/20 to-emerald-500/5",
    border: "border-emerald-500/30",
  },
];

const fadeUp = {
  initial: { opacity: 0, y: 20 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true },
};

export default function AgentFlow() {
  usePageMeta({ title: "Multi-Agent Architecture — Schedulo", description: "Explore how Schedulo's AI agents collaborate for optimal scheduling decisions." });

  const { data: agentInfoList = [], isLoading } = useAgentInfo();

  return (
    <div className="min-h-screen bg-background pt-20 pb-16">
      <div className="max-w-5xl mx-auto px-4 sm:px-6">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16"
        >
          <ScheduloAssistant size="lg" glowing className="mx-auto mb-6" />
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight mb-3" data-testid="text-agent-flow-title">
            Multi-Agent Architecture
          </h1>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto mb-6">
            Explore how Schedulo's AI agents collaborate to deliver optimal scheduling decisions.
          </p>
          
          {/* Unique Value Proposition */}
          <div className="max-w-4xl mx-auto mt-8 grid md:grid-cols-3 gap-4">
            <Card className="p-4 border-blue-500/30 bg-blue-500/5">
              <div className="text-2xl font-bold text-blue-500 mb-1">10+ People</div>
              <div className="text-xs text-muted-foreground">Coordinate entire teams instantly</div>
              <div className="text-[10px] text-muted-foreground mt-2">vs Calendly: 1-on-1 only</div>
            </Card>
            <Card className="p-4 border-purple-500/30 bg-purple-500/5">
              <div className="text-2xl font-bold text-purple-500 mb-1">92% Accuracy</div>
              <div className="text-xs text-muted-foreground">ML learns your preferences</div>
              <div className="text-[10px] text-muted-foreground mt-2">vs Calendly: Manual setup</div>
            </Card>
            <Card className="p-4 border-emerald-500/30 bg-emerald-500/5">
              <div className="text-2xl font-bold text-emerald-500 mb-1">3 Seconds</div>
              <div className="text-xs text-muted-foreground">Find optimal time for everyone</div>
              <div className="text-[10px] text-muted-foreground mt-2">vs Email: Hours/days</div>
            </Card>
          </div>
        </motion.div>

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent"></div>
            <p className="mt-4 text-muted-foreground">Loading agent information...</p>
          </div>
        )}

        {/* Agent Cards */}
        {!isLoading && (
        <div className="grid md:grid-cols-2 gap-8 mb-20">
          {agentInfoList.map((agent, i) => {
            const Icon = agentIcons[agent.type];
            return (
              <motion.div
                key={agent.type}
                {...fadeUp}
                transition={{ duration: 0.5, delay: i * 0.1 }}
              >
                <Card className="relative overflow-hidden h-full hover:border-primary/30 transition-all duration-300 group" data-testid={`card-agent-${agent.type}`}>
                  <div className={cn("absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-100 transition-opacity duration-500", agent.color)} />
                  <div className="relative p-6">
                    <div className="flex items-center gap-4 mb-4">
                      <div className={cn("w-12 h-12 rounded-xl bg-gradient-to-br flex items-center justify-center", agent.color)}>
                        <Icon className="h-6 w-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold">{agent.name}</h3>
                        <Badge variant="secondary" className="text-[10px] mt-1">
                          {agent.type.toUpperCase()} MODULE
                        </Badge>
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground leading-relaxed mb-5">
                      {agent.description}
                    </p>
                    <div className="space-y-2">
                      {agent.capabilities.map((cap) => (
                        <div key={cap} className="flex items-center gap-2 text-xs">
                          <CheckCircle2 className="h-3.5 w-3.5 text-primary shrink-0" />
                          <span className="text-muted-foreground">{cap}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </Card>
              </motion.div>
            );
          })}
        </div>
        )}

        <motion.div {...fadeUp} className="mb-8 text-center">
          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight mb-3">Information Flow</h2>
          <p className="text-muted-foreground max-w-xl mx-auto">
            Privacy-preserving coordination ensures raw calendar data never leaves each attendee's local agent.
          </p>
        </motion.div>

        <div className="max-w-lg mx-auto space-y-0">
          {flowSteps.map((step, i) => (
            <motion.div
              key={step.label}
              {...fadeUp}
              transition={{ duration: 0.5, delay: i * 0.1 }}
            >
              <div className="flex items-start gap-4">
                <div className="flex flex-col items-center">
                  <div className={cn(
                    "w-10 h-10 rounded-full border-2 flex items-center justify-center bg-background",
                    step.border
                  )}>
                    <step.icon className="h-4 w-4 text-foreground" />
                  </div>
                  {i < flowSteps.length - 1 && (
                    <div className="w-px h-12 bg-border my-2 relative">
                      <motion.div
                        className="absolute inset-0 w-full bg-primary/40"
                        initial={{ scaleY: 0, originY: 0 }}
                        whileInView={{ scaleY: 1 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.5, delay: 0.3 + i * 0.1 }}
                      />
                    </div>
                  )}
                </div>
                <div className="pt-1.5 pb-4">
                  <div className="text-sm font-semibold mb-1">{step.label}</div>
                  <div className="text-xs text-muted-foreground leading-relaxed max-w-sm">{step.desc}</div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        <motion.div {...fadeUp} className="mt-20 space-y-8">
          {/* Privacy Card */}
          <Card className="p-8 text-center border-primary/20 bg-gradient-to-b from-primary/5 to-transparent">
            <Shield className="h-8 w-8 text-primary mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Privacy by Design</h3>
            <p className="text-sm text-muted-foreground max-w-lg mx-auto leading-relaxed mb-6">
              Each attendee's scheduling intelligence runs locally. Only constrained availability signals — never raw calendar data — are shared with the coordination layer. This ensures privacy while enabling optimal group scheduling.
            </p>
            <Link href="/dashboard">
              <Button size="lg" className="gap-2">
                Try the Demo
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </Card>

          {/* What Makes Us Different */}
          <Card className="p-8 border-amber-500/20 bg-gradient-to-b from-amber-500/5 to-transparent">
            <div className="text-center mb-6">
              <Zap className="h-8 w-8 text-amber-500 mx-auto mb-3" />
              <h3 className="text-xl font-bold mb-2">What Makes Schedulo Unique</h3>
              <p className="text-sm text-muted-foreground">
                Not just another scheduling link — a complete AI coordination platform
              </p>
            </div>
            
            <div className="grid md:grid-cols-2 gap-6 max-w-3xl mx-auto">
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center shrink-0 mt-0.5">
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold mb-1">Multi-Party Coordination</div>
                    <div className="text-xs text-muted-foreground">
                      Schedule with 10+ people instantly. Calendly can't do this.
                    </div>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center shrink-0 mt-0.5">
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold mb-1">AI Learning</div>
                    <div className="text-xs text-muted-foreground">
                      Learns you prefer 2pm meetings (94% acceptance) vs 8am (12%).
                    </div>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center shrink-0 mt-0.5">
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold mb-1">Smart External Links</div>
                    <div className="text-xs text-muted-foreground">
                      Pre-coordinates your team, shows external users only 3-5 best times.
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center shrink-0 mt-0.5">
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold mb-1">Cross-Company Federation</div>
                    <div className="text-xs text-muted-foreground">
                      Schedule across organizations without sharing calendars.
                    </div>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center shrink-0 mt-0.5">
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold mb-1">Explainable AI</div>
                    <div className="text-xs text-muted-foreground">
                      Every recommendation comes with reasoning and confidence scores.
                    </div>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center shrink-0 mt-0.5">
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold mb-1">Conflict Resolution</div>
                    <div className="text-xs text-muted-foreground">
                      Handles timezones, priorities, and edge cases automatically.
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-8 p-4 bg-background/50 rounded-lg border border-border">
              <div className="text-xs text-muted-foreground text-center">
                <span className="font-semibold text-foreground">Real-world example:</span> Schedule with 2 teammates + 1 external person. 
                Calendly: 2-3 days of emails. Schedulo: 30 seconds + their response.
              </div>
            </div>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
