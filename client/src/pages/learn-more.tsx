import { motion } from "framer-motion";
import { Link } from "wouter";
import { Button } from "@/components/ui/button";
import { ScheduloAssistant } from "@/components/schedulo/assistant";
import { usePageMeta } from "@/hooks/use-page-meta";
import {
  ArrowRight,
  Shield,
  Lock,
  Eye,
  Brain,
  Zap,
  Users,
  TrendingUp,
  Clock,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Sparkles,
  Globe,
  Calendar,
  MessageSquare,
} from "lucide-react";

const fadeUp = {
  initial: { opacity: 0, y: 30 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-50px" },
  transition: { duration: 0.6 },
};

const problemPoints = [
  {
    icon: MessageSquare,
    title: "Email Tennis",
    description: "Average of 8-12 emails to schedule a 4-person meeting",
    impact: "2-3 hours wasted per meeting",
  },
  {
    icon: Clock,
    title: "Time Drain",
    description: "Professionals spend 2-3 hours per week just scheduling",
    impact: "120+ hours per year lost",
  },
  {
    icon: Users,
    title: "Coordination Chaos",
    description: "More attendees = exponentially more complexity",
    impact: "Meetings delayed by days",
  },
  {
    icon: Globe,
    title: "Timezone Confusion",
    description: "Distributed teams struggle with fair scheduling",
    impact: "Someone always loses",
  },
];

const traditionalVsSchedulo = [
  {
    aspect: "Time to Schedule",
    traditional: "Hours to days",
    schedulo: "3-5 seconds",
    improvement: "1000x faster",
  },
  {
    aspect: "Privacy",
    traditional: "Full calendar access required",
    schedulo: "Zero calendar details shared",
    improvement: "Complete privacy",
  },
  {
    aspect: "Intelligence",
    traditional: "Manual preference tracking",
    schedulo: "ML learns automatically",
    improvement: "85%+ accuracy",
  },
  {
    aspect: "Scalability",
    traditional: "Breaks with 4+ people",
    schedulo: "Handles any group size",
    improvement: "Unlimited scale",
  },
];

const privacyFeatures = [
  {
    icon: Lock,
    title: "Zero Calendar Sharing",
    description: "Your calendar details never leave your agent. Only availability signals are shared.",
    shared: ["Available", "Busy", "Flexible"],
    neverShared: ["Event titles", "Descriptions", "Attendees", "Locations"],
  },
  {
    icon: Shield,
    title: "Agent Isolation",
    description: "Each person has their own AI agent that only accesses their calendar.",
    shared: ["Confidence scores", "Flexibility ratings"],
    neverShared: ["Meeting patterns", "Full calendar view", "Personal data"],
  },
  {
    icon: Eye,
    title: "Privacy-Preserving Signals",
    description: "Agents negotiate using minimal information - just enough to find consensus.",
    shared: ["Time slot status", "Priority overrides"],
    neverShared: ["Why you're busy", "Who you're meeting", "Meeting content"],
  },
];

const howItWorks = [
  {
    step: 1,
    title: "Natural Language Request",
    description: "Simply describe what you need: 'Schedule Q2 planning with Sarah and Marcus next week'",
    tech: "OpenAI GPT-4 parses intent, extracts attendees, duration, and preferences",
  },
  {
    step: 2,
    title: "Personal Agent Analysis",
    description: "Each attendee's AI agent independently analyzes their calendar and learns from history",
    tech: "ML models predict acceptance probability based on 90 days of behavioral data",
  },
  {
    step: 3,
    title: "Privacy-Preserving Coordination",
    description: "Agents share only availability signals (available/busy/flexible) - never calendar details",
    tech: "Multi-agent coordinator finds consensus slots where everyone is available",
  },
  {
    step: 4,
    title: "Intelligent Ranking",
    description: "OpenAI analyzes all factors and generates human-readable explanations",
    tech: "Considers preferences, timezones, working hours, and learned patterns",
  },
  {
    step: 5,
    title: "Smart Escalation",
    description: "If confidence is low or conflicts arise, the system escalates to humans",
    tech: "Human-in-the-loop ensures critical decisions get manual review",
  },
];

const systemCapabilities = [
  {
    category: "Core Intelligence",
    features: [
      "ML-powered preference learning (85%+ accuracy)",
      "Natural language understanding via OpenAI GPT-4",
      "Real-time calendar analysis across all attendees",
      "Behavioral pattern recognition and prediction",
    ],
  },
  {
    category: "Privacy & Security",
    features: [
      "Zero calendar detail sharing between agents",
      "Privacy-preserving availability signals only",
      "Agent isolation (one agent per user)",
      "No centralized calendar access required",
    ],
  },
  {
    category: "Edge Case Handling",
    features: [
      "Timezone conflict resolution for distributed teams",
      "Working hours respect across all attendees",
      "Back-to-back meeting limit enforcement",
      "Holiday and vacation detection",
      "High-priority conflict intelligent resolution",
      "Last-minute request handling (< 24 hours)",
    ],
  },
  {
    category: "Explainability",
    features: [
      "Transparent reasoning for every recommendation",
      "Confidence scores for all predictions",
      "Human-readable explanations via OpenAI",
      "Decision cockpit showing agent analysis",
    ],
  },
];

const valuePropositions = [
  {
    icon: Clock,
    title: "Save 2-3 Hours Per Week",
    description: "Eliminate scheduling back-and-forth. Get optimal times in seconds instead of hours.",
    metric: "120+ hours saved per year",
  },
  {
    icon: Shield,
    title: "Complete Privacy Protection",
    description: "Your calendar stays private. Only you and your agent see the details.",
    metric: "Zero calendar details shared",
  },
  {
    icon: Brain,
    title: "Gets Smarter Over Time",
    description: "ML learns your preferences automatically. No manual configuration needed.",
    metric: "85%+ prediction accuracy",
  },
  {
    icon: Users,
    title: "Fair for Distributed Teams",
    description: "Timezone-aware scheduling ensures no one always gets the bad slot.",
    metric: "Balanced across timezones",
  },
  {
    icon: Zap,
    title: "Lightning Fast",
    description: "4-person meeting scheduled in 5 seconds. No more email tennis.",
    metric: "1000x faster than email",
  },
  {
    icon: TrendingUp,
    title: "Scales Effortlessly",
    description: "Works for 2 people or 20. Complexity doesn't slow it down.",
    metric: "Unlimited attendees",
  },
];

export default function LearnMore() {
  usePageMeta({ 
    title: "Learn More — Schedulo", 
    description: "Discover how Schedulo solves scheduling challenges with privacy-preserving AI" 
  });

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative pt-32 pb-24 px-4 sm:px-6 overflow-hidden">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[800px] rounded-full bg-primary/5 blur-3xl" />
        </div>

        <div className="max-w-5xl mx-auto text-center relative z-10">
          <motion.div {...fadeUp} className="mb-8">
            <ScheduloAssistant size="xl" glowing className="mx-auto mb-8" />
          </motion.div>

          <motion.div {...fadeUp} transition={{ duration: 0.6, delay: 0.15 }}>
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-primary/20 bg-primary/5 text-primary text-sm font-medium mb-6">
              <Sparkles className="h-3.5 w-3.5" />
              Privacy-Preserving Multi-Agent AI
            </div>
          </motion.div>

          <motion.h1
            {...fadeUp}
            transition={{ duration: 0.6, delay: 0.25 }}
            className="text-5xl sm:text-6xl font-bold tracking-tight leading-[1.1] mb-6"
          >
            Scheduling Solved with
            <br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary to-purple-500">
              Privacy-First AI
            </span>
          </motion.h1>

          <motion.p
            {...fadeUp}
            transition={{ duration: 0.6, delay: 0.35 }}
            className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed"
          >
            Schedulo uses multiple AI agents that learn your preferences, coordinate privately, 
            and find optimal meeting times in seconds - without ever sharing your calendar details.
          </motion.p>

          <motion.div
            {...fadeUp}
            transition={{ duration: 0.6, delay: 0.45 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Link href="/try-demo">
              <Button size="lg" className="gap-2 text-base px-8">
                Try Demo
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/agents">
              <Button variant="outline" size="lg" className="gap-2 text-base px-8">
                View Agent Flow
              </Button>
            </Link>
          </motion.div>
        </div>
      </section>

      {/* The Problem */}
      <section className="py-24 px-4 sm:px-6 border-t border-border/50">
        <div className="max-w-6xl mx-auto">
          <motion.div {...fadeUp} className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
              The Traditional Scheduling Problem
            </h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              Meeting coordination is broken. Here's why:
            </p>
          </motion.div>

          <div className="grid sm:grid-cols-2 gap-6">
            {problemPoints.map((problem, i) => (
              <motion.div
                key={problem.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                className="rounded-xl border border-destructive/20 bg-destructive/5 p-6"
              >
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-lg bg-destructive/10 flex items-center justify-center flex-shrink-0">
                    <problem.icon className="h-5 w-5 text-destructive" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold mb-1">{problem.title}</h3>
                    <p className="text-sm text-muted-foreground mb-2">{problem.description}</p>
                    <p className="text-sm font-medium text-destructive">{problem.impact}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Traditional vs Schedulo */}
      <section className="py-24 px-4 sm:px-6 bg-card/50">
        <div className="max-w-6xl mx-auto">
          <motion.div {...fadeUp} className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
              Traditional Tools vs Schedulo
            </h2>
            <p className="text-muted-foreground text-lg">
              See how we solve the challenges differently
            </p>
          </motion.div>

          <motion.div
            {...fadeUp}
            className="rounded-xl border border-border/60 bg-card overflow-hidden"
          >
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="text-left p-4 font-semibold">Aspect</th>
                    <th className="text-left p-4 font-semibold">Traditional Tools</th>
                    <th className="text-left p-4 font-semibold">Schedulo</th>
                    <th className="text-left p-4 font-semibold">Improvement</th>
                  </tr>
                </thead>
                <tbody>
                  {traditionalVsSchedulo.map((row, i) => (
                    <motion.tr
                      key={row.aspect}
                      initial={{ opacity: 0 }}
                      whileInView={{ opacity: 1 }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.3, delay: i * 0.1 }}
                      className="border-t border-border/50"
                    >
                      <td className="p-4 font-medium">{row.aspect}</td>
                      <td className="p-4 text-muted-foreground">
                        <div className="flex items-center gap-2">
                          <XCircle className="h-4 w-4 text-destructive flex-shrink-0" />
                          {row.traditional}
                        </div>
                      </td>
                      <td className="p-4 text-muted-foreground">
                        <div className="flex items-center gap-2">
                          <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0" />
                          {row.schedulo}
                        </div>
                      </td>
                      <td className="p-4">
                        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium">
                          <TrendingUp className="h-3 w-3" />
                          {row.improvement}
                        </span>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-24 px-4 sm:px-6 border-t border-border/50">
        <div className="max-w-6xl mx-auto">
          <motion.div {...fadeUp} className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
              How Schedulo Works
            </h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              Five intelligent steps from request to scheduled meeting
            </p>
          </motion.div>

          <div className="space-y-8">
            {howItWorks.map((step, i) => (
              <motion.div
                key={step.step}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                className="relative"
              >
                <div className="flex gap-6">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 rounded-full bg-primary/10 border-2 border-primary flex items-center justify-center">
                      <span className="text-lg font-bold text-primary">{step.step}</span>
                    </div>
                  </div>
                  <div className="flex-1 rounded-xl border border-border/60 bg-card p-6">
                    <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                    <p className="text-muted-foreground mb-3">{step.description}</p>
                    <div className="flex items-start gap-2 text-sm">
                      <Sparkles className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
                      <span className="text-primary/80">{step.tech}</span>
                    </div>
                  </div>
                </div>
                {i < howItWorks.length - 1 && (
                  <div className="absolute left-6 top-12 bottom-0 w-0.5 bg-border/50" />
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Privacy Features */}
      <section className="py-24 px-4 sm:px-6 bg-card/50">
        <div className="max-w-6xl mx-auto">
          <motion.div {...fadeUp} className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
              Privacy by Design
            </h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              Your calendar details never leave your agent. Here's how we protect your privacy:
            </p>
          </motion.div>

          <div className="grid lg:grid-cols-3 gap-6">
            {privacyFeatures.map((feature, i) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                className="rounded-xl border border-border/60 bg-card p-6"
              >
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                <p className="text-sm text-muted-foreground mb-4">{feature.description}</p>
                
                <div className="space-y-3">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle2 className="h-4 w-4 text-primary" />
                      <span className="text-sm font-medium">What's Shared</span>
                    </div>
                    <div className="pl-6 space-y-1">
                      {feature.shared.map((item) => (
                        <div key={item} className="text-xs text-muted-foreground">• {item}</div>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <XCircle className="h-4 w-4 text-destructive" />
                      <span className="text-sm font-medium">Never Shared</span>
                    </div>
                    <div className="pl-6 space-y-1">
                      {feature.neverShared.map((item) => (
                        <div key={item} className="text-xs text-muted-foreground">• {item}</div>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* System Capabilities */}
      <section className="py-24 px-4 sm:px-6 border-t border-border/50">
        <div className="max-w-6xl mx-auto">
          <motion.div {...fadeUp} className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
              Complete System Capabilities
            </h2>
            <p className="text-muted-foreground text-lg">
              Everything Schedulo can do for you
            </p>
          </motion.div>

          <div className="grid sm:grid-cols-2 gap-6">
            {systemCapabilities.map((category, i) => (
              <motion.div
                key={category.category}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                className="rounded-xl border border-border/60 bg-card p-6"
              >
                <h3 className="text-lg font-semibold mb-4">{category.category}</h3>
                <ul className="space-y-2">
                  {category.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-2 text-sm text-muted-foreground">
                      <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Value Propositions */}
      <section className="py-24 px-4 sm:px-6 bg-card/50">
        <div className="max-w-6xl mx-auto">
          <motion.div {...fadeUp} className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
              Why Choose Schedulo
            </h2>
            <p className="text-muted-foreground text-lg">
              Real value for individuals and teams
            </p>
          </motion.div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {valuePropositions.map((value, i) => (
              <motion.div
                key={value.title}
                initial={{ opacity: 0, scale: 0.95 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.1 }}
                className="rounded-xl border border-border/60 bg-card p-6 hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5 transition-all duration-300"
              >
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <value.icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-lg font-semibold mb-2">{value.title}</h3>
                <p className="text-sm text-muted-foreground mb-3">{value.description}</p>
                <div className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium">
                  {value.metric}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-4 sm:px-6 border-t border-border/50">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div {...fadeUp}>
            <ScheduloAssistant size="lg" glowing className="mx-auto mb-8" />
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
              Experience the Future of Scheduling
            </h2>
            <p className="text-muted-foreground text-lg max-w-xl mx-auto mb-8">
              See how privacy-preserving AI can transform your meeting coordination
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/try-demo">
                <Button size="lg" className="gap-2 text-base px-10">
                  Try Interactive Demo
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
              <Link href="/dashboard">
                <Button variant="outline" size="lg" className="gap-2 text-base px-10">
                  Go to Dashboard
                </Button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
