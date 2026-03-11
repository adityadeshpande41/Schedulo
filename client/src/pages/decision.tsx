import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { ScheduloAssistant } from "@/components/schedulo/assistant";
import { usePageMeta } from "@/hooks/use-page-meta";
import { mockApi } from "@/data/mock";
import {
  Star,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  CalendarSearch,
  Brain,
  Users,
  Cpu,
  ThumbsUp,
  ThumbsDown,
  Clock,
  ArrowRight,
  Sparkles,
  BarChart3,
} from "lucide-react";
import { cn } from "@/lib/utils";

const agentIconMap: Record<string, typeof Cpu> = {
  calendar: CalendarSearch,
  behavior: Brain,
  coordination: Users,
  orchestrator: Cpu,
};

const agentColorMap: Record<string, string> = {
  calendar: "text-blue-500",
  behavior: "text-purple-500",
  coordination: "text-amber-500",
  orchestrator: "text-emerald-500",
};

function formatTime(dateStr: string) {
  return new Date(dateStr).toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit", hour12: true });
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });
}

export default function Decision() {
  usePageMeta({ title: "AI Decision Cockpit — Schedulo", description: "See why Schedulo recommended a specific meeting slot with full explainability." });

  const { data: decision, isLoading } = useQuery({
    queryKey: ["decision", "m2"],
    queryFn: () => mockApi.getMeetingDecision("m2"),
  });

  if (isLoading || !decision) {
    return (
      <div className="min-h-screen bg-background pt-20 pb-16">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 space-y-6">
          <Skeleton className="h-10 w-64" />
          <Skeleton className="h-48 rounded-xl" />
          <Skeleton className="h-64 rounded-xl" />
        </div>
      </div>
    );
  }

  const rec = decision.recommendedSlot;

  return (
    <div className="min-h-screen bg-background pt-20 pb-16">
      <div className="max-w-5xl mx-auto px-4 sm:px-6">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center gap-3 mb-2">
            <Sparkles className="h-5 w-5 text-primary" />
            <h1 className="text-2xl font-bold tracking-tight" data-testid="text-decision-title">AI Decision Cockpit</h1>
          </div>
          <p className="text-muted-foreground text-sm">{decision.requestSummary}</p>
        </motion.div>

        <div className="grid lg:grid-cols-5 gap-6">
          <div className="lg:col-span-3 space-y-6">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
              <Card className="p-6 border-primary/30 bg-gradient-to-b from-primary/5 to-transparent" data-testid="card-recommendation">
                <div className="flex items-center gap-2 mb-4">
                  <Star className="h-4 w-4 text-primary" />
                  <span className="text-sm font-semibold text-primary">Top Recommendation</span>
                </div>
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="text-lg font-bold mb-1">
                      {formatDate(rec.startTime)} · {formatTime(rec.startTime)} — {formatTime(rec.endTime)}
                    </div>
                    <p className="text-sm text-muted-foreground mb-4">{rec.reasoning}</p>
                    <div className="flex items-center gap-3">
                      <Button size="sm" className="gap-1.5" data-testid="button-approve">
                        <ThumbsUp className="h-3.5 w-3.5" />
                        Approve
                      </Button>
                      <Button variant="outline" size="sm" className="gap-1.5" data-testid="button-decline">
                        <ThumbsDown className="h-3.5 w-3.5" />
                        Decline
                      </Button>
                    </div>
                  </div>
                  <div className="text-right shrink-0">
                    <div className="text-4xl font-bold text-primary tabular-nums">{rec.score}</div>
                    <div className="text-xs text-muted-foreground">/ 100</div>
                  </div>
                </div>
              </Card>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
              <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
                Alternative Slots
              </h3>
              <div className="space-y-3">
                {decision.alternativeSlots.map((slot, i) => (
                  <motion.div
                    key={slot.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 + i * 0.06 }}
                  >
                    <Card className="p-4 hover:border-primary/20 transition-colors" data-testid={`card-alt-slot-${slot.id}`}>
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-sm font-semibold">
                              {formatDate(slot.startTime)} · {formatTime(slot.startTime)} — {formatTime(slot.endTime)}
                            </span>
                            <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
                              #{slot.rank}
                            </Badge>
                            {slot.requiresApproval && (
                              <Badge variant="secondary" className="text-[10px] px-1.5 py-0 bg-amber-500/10 text-amber-600 dark:text-amber-400 border-0">
                                Needs Approval
                              </Badge>
                            )}
                          </div>
                          <p className="text-xs text-muted-foreground">{slot.reasoning}</p>
                          {slot.conflicts.length > 0 && (
                            <div className="mt-2 flex flex-wrap gap-1.5">
                              {slot.conflicts.map((c, ci) => (
                                <span key={ci} className={cn(
                                  "text-[10px] px-2 py-0.5 rounded-full inline-flex items-center gap-0.5",
                                  c.type === "soft" ? "bg-amber-500/10 text-amber-600 dark:text-amber-400" : "bg-red-500/10 text-red-600 dark:text-red-400"
                                )}>
                                  {c.type === "soft" ? <AlertTriangle className="h-2.5 w-2.5" /> : <XCircle className="h-2.5 w-2.5" />}
                                  {c.description}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                        <div className="text-right shrink-0">
                          <div className={cn(
                            "text-xl font-bold tabular-nums",
                            slot.score >= 80 ? "text-emerald-500" : slot.score >= 60 ? "text-amber-500" : "text-muted-foreground"
                          )}>
                            {slot.score}
                          </div>
                          <div className="text-[10px] text-muted-foreground">score</div>
                        </div>
                      </div>
                    </Card>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
              <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                Tradeoffs
              </h3>
              <Card className="p-4">
                <ul className="space-y-2">
                  {decision.tradeoffs.map((t, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                      <ArrowRight className="h-3.5 w-3.5 mt-0.5 text-amber-500 shrink-0" />
                      {t}
                    </li>
                  ))}
                </ul>
              </Card>
            </motion.div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.12 }}>
              <Card className="p-5">
                <div className="flex items-center gap-2 mb-4">
                  <ScheduloAssistant size="sm" />
                  <span className="text-sm font-semibold">Confidence</span>
                </div>
                <div className="text-center mb-4">
                  <div className="text-5xl font-bold text-primary tabular-nums" data-testid="text-confidence">
                    {decision.overallConfidence}%
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">Overall confidence score</div>
                </div>
                <Progress value={decision.overallConfidence} className="h-2 mb-2" />
                <div className="flex items-center justify-between text-[10px] text-muted-foreground">
                  <span>Low</span>
                  <span>High</span>
                </div>
                {decision.approvalNeeded && (
                  <div className="mt-4 p-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
                    <div className="flex items-center gap-2 text-xs font-medium text-amber-600 dark:text-amber-400">
                      <AlertTriangle className="h-3.5 w-3.5" />
                      Approval Required
                    </div>
                    <p className="text-[11px] text-muted-foreground mt-1">{decision.approvalReason}</p>
                  </div>
                )}
                {!decision.approvalNeeded && (
                  <div className="mt-4 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                    <div className="flex items-center gap-2 text-xs font-medium text-emerald-600 dark:text-emerald-400">
                      <CheckCircle2 className="h-3.5 w-3.5" />
                      Auto-schedulable
                    </div>
                    <p className="text-[11px] text-muted-foreground mt-1">High confidence — can be scheduled automatically.</p>
                  </div>
                )}
              </Card>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
              <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                <Cpu className="h-4 w-4 text-muted-foreground" />
                Agent Insights
              </h3>
              <div className="space-y-3">
                {decision.agentInsights.map((insight, i) => {
                  const Icon = agentIconMap[insight.agent];
                  return (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: 15 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.25 + i * 0.08 }}
                    >
                      <Card className="p-4 hover:border-primary/20 transition-colors" data-testid={`card-insight-${insight.agent}`}>
                        <div className="flex items-start gap-3">
                          <Icon className={cn("h-4 w-4 mt-0.5 shrink-0", agentColorMap[insight.agent])} />
                          <div>
                            <div className="text-xs font-medium capitalize mb-0.5">{insight.agent} Agent</div>
                            <div className="text-[11px] text-muted-foreground leading-relaxed">{insight.insight}</div>
                          </div>
                        </div>
                      </Card>
                    </motion.div>
                  );
                })}
              </div>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
              <Card className="p-5 border-primary/20 bg-gradient-to-b from-primary/5 to-transparent">
                <div className="flex items-center gap-2 mb-3">
                  <Clock className="h-4 w-4 text-primary" />
                  <span className="text-sm font-semibold">Decision Summary</span>
                </div>
                <div className="text-xs text-muted-foreground leading-relaxed space-y-2">
                  <p>
                    Schedulo analyzed <strong className="text-foreground">12 open windows</strong> across all attendee calendars this week.
                  </p>
                  <p>
                    The top slot scores <strong className="text-foreground">{rec.score}/100</strong> with{" "}
                    <strong className="text-foreground">{rec.confidence}% confidence</strong>.
                    No hard conflicts detected.
                  </p>
                  <p>
                    Recommendation is based on availability alignment, behavioral preferences, and priority weight.
                  </p>
                </div>
              </Card>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}
