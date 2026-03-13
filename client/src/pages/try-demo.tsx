import { motion } from "framer-motion";
import { Link } from "wouter";
import { Button } from "@/components/ui/button";
import { ScheduloAssistant } from "@/components/schedulo/assistant";
import { usePageMeta } from "@/hooks/use-page-meta";
import {
  ArrowRight,
  Calendar,
  Clock,
  Users,
  Shield,
  Zap,
  Brain,
  CheckCircle2,
  PlayCircle,
  Sparkles,
} from "lucide-react";

const fadeUp = {
  initial: { opacity: 0, y: 30 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-50px" },
  transition: { duration: 0.6 },
};

const demoFeatures = [
  {
    icon: Calendar,
    title: "Smart Calendar Analysis",
    description: "Watch AI agents analyze multiple calendars simultaneously, detecting conflicts and finding optimal windows in real-time.",
  },
  {
    icon: Brain,
    title: "Preference Learning",
    description: "See how the system learns from historical data - time preferences, meeting patterns, and rescheduling behavior.",
  },
  {
    icon: Users,
    title: "Multi-Agent Negotiation",
    description: "Experience privacy-preserving coordination where each person's agent negotiates without sharing calendar details.",
  },
  {
    icon: Shield,
    title: "Privacy Protection",
    description: "Verify that calendar details stay private - only availability signals are shared between agents.",
  },
  {
    icon: Zap,
    title: "Instant Results",
    description: "Get optimal meeting times in 3-5 seconds instead of hours of back-and-forth emails.",
  },
  {
    icon: Sparkles,
    title: "Explainable AI",
    description: "Understand every recommendation with transparent reasoning and confidence scores.",
  },
];

const demoScenarios = [
  {
    title: "Simple 1:1 Meeting",
    description: "Schedule a quick sync with one person",
    time: "~2 seconds",
    complexity: "Basic",
  },
  {
    title: "Team Meeting (3-4 people)",
    description: "Coordinate across multiple calendars",
    time: "~4 seconds",
    complexity: "Moderate",
  },
  {
    title: "Cross-Timezone Meeting",
    description: "Fair scheduling for distributed teams",
    time: "~5 seconds",
    complexity: "Advanced",
  },
  {
    title: "High-Priority Conflict",
    description: "See intelligent conflict resolution",
    time: "~6 seconds",
    complexity: "Complex",
  },
];

const whatYouWillSee = [
  "Real-time agent execution with live status updates",
  "ML-powered preference predictions with confidence scores",
  "Privacy-preserving availability signals (no calendar details shared)",
  "Intelligent ranking with OpenAI-generated explanations",
  "Edge case handling (timezones, conflicts, working hours)",
  "Human escalation when confidence is low",
];

export default function TryDemo() {
  usePageMeta({ 
    title: "Try Demo — Schedulo", 
    description: "Experience AI-powered multi-agent scheduling in action" 
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
              <PlayCircle className="h-3.5 w-3.5" />
              Interactive Demo
            </div>
          </motion.div>

          <motion.h1
            {...fadeUp}
            transition={{ duration: 0.6, delay: 0.25 }}
            className="text-5xl sm:text-6xl font-bold tracking-tight leading-[1.1] mb-6"
          >
            Experience AI Scheduling
            <br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary to-purple-500">
              In Real-Time
            </span>
          </motion.h1>

          <motion.p
            {...fadeUp}
            transition={{ duration: 0.6, delay: 0.35 }}
            className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed"
          >
            Watch multiple AI agents collaborate to find the perfect meeting time. 
            See privacy-preserving coordination, ML-powered predictions, and intelligent reasoning in action.
          </motion.p>

          <motion.div
            {...fadeUp}
            transition={{ duration: 0.6, delay: 0.45 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Link href="/dashboard">
              <Button size="lg" className="gap-2 text-base px-8">
                Launch Demo
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/agents">
              <Button variant="outline" size="lg" className="gap-2 text-base px-8">
                View Agent Flow
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </motion.div>
        </div>
      </section>

      {/* What You'll Experience */}
      <section className="py-24 px-4 sm:px-6 border-t border-border/50">
        <div className="max-w-6xl mx-auto">
          <motion.div {...fadeUp} className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
              What You'll Experience
            </h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              The demo showcases all core capabilities of our multi-agent AI system
            </p>
          </motion.div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {demoFeatures.map((feature, i) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                className="group rounded-xl border border-border/60 bg-card p-6 transition-all duration-300 hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5"
              >
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Demo Scenarios */}
      <section className="py-24 px-4 sm:px-6 bg-card/50">
        <div className="max-w-6xl mx-auto">
          <motion.div {...fadeUp} className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
              Try Different Scenarios
            </h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              Test the system with various complexity levels
            </p>
          </motion.div>

          <div className="grid sm:grid-cols-2 gap-6">
            {demoScenarios.map((scenario, i) => (
              <motion.div
                key={scenario.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                className="rounded-xl border border-border/60 bg-card p-6 hover:border-primary/30 transition-all duration-300"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold mb-1">{scenario.title}</h3>
                    <p className="text-sm text-muted-foreground">{scenario.description}</p>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <span className="text-xs font-mono text-primary">{scenario.time}</span>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary">
                      {scenario.complexity}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* What You'll See */}
      <section className="py-24 px-4 sm:px-6 border-t border-border/50">
        <div className="max-w-4xl mx-auto">
          <motion.div {...fadeUp} className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
              Behind the Scenes
            </h2>
            <p className="text-muted-foreground text-lg">
              The demo reveals how our AI agents work together
            </p>
          </motion.div>

          <motion.div
            {...fadeUp}
            className="rounded-xl border border-border/60 bg-card p-8"
          >
            <div className="space-y-4">
              {whatYouWillSee.map((item, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: i * 0.1 }}
                  className="flex items-start gap-3"
                >
                  <CheckCircle2 className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                  <span className="text-muted-foreground">{item}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Performance Metrics */}
      <section className="py-24 px-4 sm:px-6 bg-card/50">
        <div className="max-w-6xl mx-auto">
          <motion.div {...fadeUp} className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
              Real Performance Metrics
            </h2>
            <p className="text-muted-foreground text-lg">
              See actual system performance in the demo
            </p>
          </motion.div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { label: "Agent Execution", value: "~500ms", desc: "Per personal agent" },
              { label: "ML Prediction", value: "~50ms", desc: "Per time slot" },
              { label: "Total Workflow", value: "3-5s", desc: "For 3 attendees" },
              { label: "ML Accuracy", value: "85%+", desc: "After 90 days" },
            ].map((metric, i) => (
              <motion.div
                key={metric.label}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.1 }}
                className="rounded-xl border border-border/60 bg-card p-6 text-center"
              >
                <div className="text-3xl font-bold text-primary mb-2">{metric.value}</div>
                <div className="text-sm font-semibold mb-1">{metric.label}</div>
                <div className="text-xs text-muted-foreground">{metric.desc}</div>
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
              Ready to See It in Action?
            </h2>
            <p className="text-muted-foreground text-lg max-w-xl mx-auto mb-8">
              Launch the interactive demo and experience the future of AI-powered scheduling
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/dashboard">
                <Button size="lg" className="gap-2 text-base px-10">
                  Launch Demo Now
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
              <Link href="/learn-more">
                <Button variant="outline" size="lg" className="gap-2 text-base px-10">
                  Learn More
                </Button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
