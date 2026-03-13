import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Calendar } from "@/components/ui/calendar";
import { ScheduloAssistant } from "@/components/schedulo/assistant";
import { CalendarConnect } from "@/components/schedulo/calendar-connect";
import { usePageMeta } from "@/hooks/use-page-meta";
import { useUpcomingMeetings } from "@/hooks/use-meetings";
import { useAgentActivity } from "@/hooks/use-agents";
import { useUserPreferences } from "@/hooks/use-preferences";
import { useCreateScheduleRequest } from "@/hooks/use-schedule";
import { mockUsers } from "@/data/mock";
import type { TimeSlot } from "@/types/schedulo";
import {
  Calendar as CalendarIcon,
  Clock,
  Users,
  Video,
  MapPin,
  Star,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Sparkles,
  CalendarSearch,
  Brain,
  Cpu,
  Sun,
  CalendarX,
  ArrowUp,
  Triangle,
  Search,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { format } from "date-fns";

const agentMeta: Record<string, { icon: typeof Cpu; color: string; label: string }> = {
  calendar: { icon: CalendarSearch, color: "text-blue-500", label: "Calendar Agent" },
  behavior: { icon: Brain, color: "text-purple-500", label: "Behavior Agent" },
  coordination: { icon: Users, color: "text-amber-500", label: "Coordination Agent" },
  orchestrator: { icon: Cpu, color: "text-emerald-500", label: "Orchestrator" },
};

const statusColors: Record<string, string> = {
  confirmed: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
  pending: "bg-amber-500/10 text-amber-600 dark:text-amber-400",
  rescheduled: "bg-blue-500/10 text-blue-600 dark:text-blue-400",
  cancelled: "bg-red-500/10 text-red-600 dark:text-red-400",
};

const priorityColors: Record<string, string> = {
  high: "bg-red-500/10 text-red-600 dark:text-red-400",
  medium: "bg-amber-500/10 text-amber-600 dark:text-amber-400",
  low: "bg-blue-500/10 text-blue-600 dark:text-blue-400",
};

const prefIcons: Record<string, typeof Sun> = {
  sun: Sun,
  "calendar-x": CalendarX,
  "arrow-up": ArrowUp,
  clock: Clock,
  "alert-triangle": Triangle,
  brain: Brain,
};

function formatTime(dateStr: string) {
  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) {
      return "Invalid Time";
    }
    return date.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit", hour12: true });
  } catch (e) {
    return "Invalid Time";
  }
}

function formatDate(dateStr: string) {
  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) {
      return "Invalid Date";
    }
    return date.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });
  } catch (e) {
    return "Invalid Date";
  }
}

export default function Dashboard() {
  usePageMeta({ title: "Dashboard — Schedulo", description: "Manage your AI-powered schedule with intelligent meeting coordination." });

  // Allow switching between users (demo mode)
  const [selectedUserId, setSelectedUserId] = useState(import.meta.env.VITE_DEFAULT_USER_ID || "u1");
  
  // Check URL params for user_id (from OAuth callback)
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const userIdFromUrl = params.get('user_id');
    if (userIdFromUrl) {
      setSelectedUserId(userIdFromUrl);
      // Clean up URL
      window.history.replaceState({}, '', '/dashboard');
    }
  }, []);
  
  const userId = selectedUserId;
  
  const { data: meetings, isLoading: meetingsLoading } = useUpcomingMeetings(userId);
  
  // Debug: log meetings data
  if (meetings) {
    console.log('Meetings data:', meetings);
    console.log('First meeting:', meetings[0]);
  }
  const { data: agents, isLoading: agentsLoading } = useAgentActivity();
  const { data: prefs, isLoading: prefsLoading } = useUserPreferences(userId);
  
  const createSchedule = useCreateScheduleRequest();

  const [showSlots, setShowSlots] = useState(false);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [slots, setSlots] = useState<TimeSlot[] | null>(null);
  const [meetingTitle, setMeetingTitle] = useState("New Meeting");
  const [attendeesInput, setAttendeesInput] = useState("");
  const [dateRange, setDateRange] = useState<{ from: Date | undefined; to: Date | undefined }>({
    from: new Date(),
    to: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days from now
  });

  const handleFindSlots = async () => {
    setLoadingSlots(true);
    setShowSlots(true);
    try {
      // Get user's timezone
      const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
      
      // Prepare date range
      let timeRange = undefined;
      if (dateRange.from && dateRange.to) {
        const startStr = format(dateRange.from, "yyyy-MM-dd");
        const endStr = format(dateRange.to, "yyyy-MM-dd");
        
        timeRange = {
          start: `${startStr}T00:00:00`,
          end: `${endStr}T23:59:59`,
          timezone: userTimezone
        };
      }
      
      const result = await createSchedule.mutateAsync({
        title: meetingTitle,
        attendees: [userId],
        duration: 30,
        priority: "medium",
        type: "team_sync",
        preferredTimeRange: timeRange
      });
      console.log("API Response:", result);
      console.log("Slots:", result.recommended_slots);
      setSlots(result.recommended_slots);
    } catch (error) {
      console.error("Error finding slots:", error);
    } finally {
      setLoadingSlots(false);
    }
  };
  
  const handleSelectSlot = async (slot: TimeSlot) => {
    try {
      // Parse attendees from input
      const attendeeEmails = attendeesInput
        .split(',')
        .map(email => email.trim())
        .filter(email => email.length > 0);
      
      // Call the confirm endpoint with meeting details
      const response = await fetch(`http://localhost:8000/api/schedule/slots/${slot.id}/confirm`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title: meetingTitle,
          attendees: attendeeEmails,
        }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        alert(`✅ Meeting booked!\n\n📅 ${formatDate(slot.start_time)} at ${formatTime(slot.start_time)}\n\n${data.google_event_id ? '✓ Added to your Google Calendar\n✓ Calendar invites sent' : '⚠️ Added to Schedulo (Google Calendar sync failed)'}`);
        
        // Refresh meetings list
        window.location.reload();
      } else {
        throw new Error(data.detail || "Failed to book meeting");
      }
    } catch (error) {
      console.error("Error booking slot:", error);
      alert("❌ Failed to book meeting. Please try again.");
    }
  };

  return (
    <div className="min-h-screen bg-background pt-20 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold tracking-tight mb-1" data-testid="text-dashboard-title">Dashboard</h1>
              <p className="text-muted-foreground text-sm">Manage your schedule with AI-powered intelligence.</p>
            </div>
            
            {/* User Switcher (Demo Mode) */}
            <div className="flex items-center gap-2">
              <Label htmlFor="user-select" className="text-xs text-muted-foreground">View as:</Label>
              <Select value={selectedUserId} onValueChange={setSelectedUserId}>
                <SelectTrigger className="w-[180px] h-9" id="user-select">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {mockUsers.map((user) => (
                    <SelectItem key={user.id} value={user.id}>
                      {user.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
              <Tabs defaultValue="upcoming" className="w-full">
                <TabsList className="mb-4">
                  <TabsTrigger value="upcoming" data-testid="tab-upcoming">Upcoming</TabsTrigger>
                  <TabsTrigger value="schedule" data-testid="tab-schedule">Schedule</TabsTrigger>
                </TabsList>

                <TabsContent value="upcoming">
                  <div className="space-y-3">
                    {meetingsLoading ? (
                      Array.from({ length: 3 }).map((_, i) => (
                        <Skeleton key={i} className="h-24 rounded-xl" />
                      ))
                    ) : (
                      meetings?.map((m, i) => (
                        <motion.div
                          key={m.id}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: i * 0.05 }}
                        >
                          <Card className="p-4 hover:border-primary/20 transition-colors" data-testid={`card-meeting-${m.id}`}>
                            <div className="flex items-start justify-between gap-4">
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1.5">
                                  <h3 className="font-semibold text-sm truncate">{m.title}</h3>
                                  <Badge variant="secondary" className={cn("text-[10px] px-1.5 py-0 shrink-0", statusColors[m.status])}>
                                    {m.status}
                                  </Badge>
                                  <Badge variant="secondary" className={cn("text-[10px] px-1.5 py-0 shrink-0", priorityColors[m.priority])}>
                                    {m.priority}
                                  </Badge>
                                </div>
                                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                                  <span className="flex items-center gap-1">
                                    <CalendarIcon className="h-3 w-3" />
                                    {formatDate(m.start_time)}
                                  </span>
                                  <span className="flex items-center gap-1">
                                    <Clock className="h-3 w-3" />
                                    {formatTime(m.start_time)} — {formatTime(m.end_time)}
                                  </span>
                                  {m.location && (
                                    <span className="flex items-center gap-1">
                                      {m.location.includes("Virtual") ? <Video className="h-3 w-3" /> : <MapPin className="h-3 w-3" />}
                                      {m.location}
                                    </span>
                                  )}
                                </div>
                                <div className="flex items-center gap-1 mt-2">
                                  {m.attendees.slice(0, 4).map((a) => (
                                    <div
                                      key={a.id}
                                      className="w-6 h-6 rounded-full bg-primary/10 border border-background flex items-center justify-center text-[10px] font-medium text-primary -ml-1 first:ml-0"
                                      title={a.name}
                                    >
                                      {a.name.split(" ").map((n) => n[0]).join("")}
                                    </div>
                                  ))}
                                  {m.attendees.length > 4 && (
                                    <div className="w-6 h-6 rounded-full bg-muted border border-background flex items-center justify-center text-[10px] font-medium text-muted-foreground -ml-1">
                                      +{m.attendees.length - 4}
                                    </div>
                                  )}
                                </div>
                              </div>
                              <div className="text-right shrink-0">
                                <div className="text-2xl font-bold text-primary tabular-nums">{formatTime(m.start_time).split(" ")[0]}</div>
                                <div className="text-[10px] text-muted-foreground uppercase">{formatTime(m.start_time).split(" ")[1]}</div>
                              </div>
                            </div>
                          </Card>
                        </motion.div>
                      ))
                    )}
                  </div>
                </TabsContent>

                <TabsContent value="schedule">
                  <Card className="p-6">
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="title" className="text-sm font-medium">Meeting Title</Label>
                        <Input 
                          id="title" 
                          placeholder="e.g., Product Review" 
                          className="mt-1.5" 
                          data-testid="input-meeting-title"
                          value={meetingTitle}
                          onChange={(e) => setMeetingTitle(e.target.value)}
                        />
                      </div>
                      <div>
                        <Label className="text-sm font-medium">Date Range</Label>
                        <Popover>
                          <PopoverTrigger asChild>
                            <Button
                              variant="outline"
                              className={cn(
                                "w-full mt-1.5 justify-start text-left font-normal",
                                !dateRange.from && "text-muted-foreground"
                              )}
                            >
                              <CalendarIcon className="mr-2 h-4 w-4" />
                              {dateRange.from ? (
                                dateRange.to ? (
                                  <>
                                    {format(dateRange.from, "LLL dd, y")} -{" "}
                                    {format(dateRange.to, "LLL dd, y")}
                                  </>
                                ) : (
                                  format(dateRange.from, "LLL dd, y")
                                )
                              ) : (
                                <span>Pick a date range</span>
                              )}
                            </Button>
                          </PopoverTrigger>
                          <PopoverContent className="w-auto p-0" align="start">
                            <Calendar
                              initialFocus
                              mode="range"
                              defaultMonth={dateRange.from}
                              selected={{ from: dateRange.from, to: dateRange.to }}
                              onSelect={(range) => setDateRange({ from: range?.from, to: range?.to })}
                              numberOfMonths={2}
                            />
                          </PopoverContent>
                        </Popover>
                        <p className="text-xs text-muted-foreground mt-1">
                          AI will find the best times within this date range
                        </p>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label className="text-sm font-medium">Duration</Label>
                          <Select defaultValue="30">
                            <SelectTrigger className="mt-1.5" data-testid="select-duration">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="15">15 minutes</SelectItem>
                              <SelectItem value="30">30 minutes</SelectItem>
                              <SelectItem value="45">45 minutes</SelectItem>
                              <SelectItem value="60">60 minutes</SelectItem>
                              <SelectItem value="90">90 minutes</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label className="text-sm font-medium">Priority</Label>
                          <Select defaultValue="medium">
                            <SelectTrigger className="mt-1.5" data-testid="select-priority">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="high">High</SelectItem>
                              <SelectItem value="medium">Medium</SelectItem>
                              <SelectItem value="low">Low</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                      <div>
                        <Label className="text-sm font-medium">Meeting Type</Label>
                        <Select defaultValue="team_sync">
                          <SelectTrigger className="mt-1.5" data-testid="select-type">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="team_sync">Team Sync</SelectItem>
                            <SelectItem value="one_on_one">1:1</SelectItem>
                            <SelectItem value="client_call">Client Call</SelectItem>
                            <SelectItem value="standup">Standup</SelectItem>
                            <SelectItem value="workshop">Workshop</SelectItem>
                            <SelectItem value="interview">Interview</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label className="text-sm font-medium">Attendees</Label>
                        <div className="mt-1.5">
                          <Input 
                            placeholder="Enter email addresses (comma separated)" 
                            className="text-sm"
                            data-testid="input-attendees"
                            value={attendeesInput}
                            onChange={(e) => setAttendeesInput(e.target.value)}
                          />
                          <p className="text-xs text-muted-foreground mt-1">
                            Add attendee email addresses to check their availability
                          </p>
                        </div>
                      </div>
                      <Button onClick={handleFindSlots} className="w-full gap-2" data-testid="button-find-slots">
                        <Search className="h-4 w-4" />
                        Find Best Slots
                      </Button>
                    </div>
                  </Card>

                  <AnimatePresence>
                    {showSlots && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        className="mt-6 space-y-3"
                      >
                        <h3 className="text-sm font-semibold flex items-center gap-2">
                          <Sparkles className="h-4 w-4 text-primary" />
                          Recommended Slots
                        </h3>
                        {loadingSlots ? (
                          Array.from({ length: 3 }).map((_, i) => (
                            <Skeleton key={i} className="h-20 rounded-xl" />
                          ))
                        ) : (
                          slots?.map((slot, i) => (
                            <SlotCard key={slot.id} slot={slot} index={i} onSelect={handleSelectSlot} />
                          ))
                        )}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </TabsContent>
              </Tabs>
            </motion.div>

            <CalendarConnect userId={userId} />

            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
              <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                <Users className="h-4 w-4 text-muted-foreground" />
                Scheduling Preferences
              </h3>
              <div className="grid sm:grid-cols-2 gap-3">
                {prefsLoading ? (
                  Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-20 rounded-xl" />)
                ) : (
                  prefs?.filter(p => p.active).map((pref, i) => {
                    const Icon = prefIcons[pref.icon] || Star;
                    return (
                      <motion.div
                        key={pref.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 + i * 0.05 }}
                      >
                        <Card className="p-4 hover:border-primary/20 transition-colors" data-testid={`card-pref-${pref.id}`}>
                          <div className="flex items-start gap-3">
                            <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                              <Icon className="h-4 w-4 text-primary" />
                            </div>
                            <div>
                              <div className="text-sm font-medium">{pref.label}</div>
                              <div className="text-xs text-muted-foreground mt-0.5">{pref.description}</div>
                            </div>
                          </div>
                        </Card>
                      </motion.div>
                    );
                  })
                )}
              </div>
            </motion.div>
          </div>

          <div className="space-y-6">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
              <Card className="p-5 border-primary/20 bg-gradient-to-b from-primary/5 to-transparent">
                <div className="flex items-center gap-3 mb-4">
                  <ScheduloAssistant size="sm" />
                  <div>
                    <div className="text-sm font-semibold">Schedulo AI</div>
                    <div className="text-[10px] text-muted-foreground">Multi-agent orchestration</div>
                  </div>
                </div>
                <div className="text-xs text-muted-foreground mb-4 leading-relaxed">
                  I'm monitoring your calendar and coordinating with your team's schedules. Here's what's happening behind the scenes.
                </div>

                <div className="space-y-3">
                  {agentsLoading ? (
                    Array.from({ length: 4 }).map((_, i) => (
                      <Skeleton key={i} className="h-12 rounded-lg" />
                    ))
                  ) : (
                    agents?.map((a, i) => {
                      const meta = agentMeta[a.agentType] || { 
                        icon: Cpu, 
                        color: "text-gray-500", 
                        label: a.agentType 
                      };
                      const Icon = meta.icon;
                      return (
                        <motion.div
                          key={a.id}
                          initial={{ opacity: 0, x: 20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 0.2 + i * 0.08 }}
                          className="flex items-start gap-3 group"
                          data-testid={`agent-${a.agentType}`}
                        >
                          <div className="relative mt-0.5">
                            <Icon className={cn("h-4 w-4", meta.color)} />
                            {a.status !== "complete" && a.status !== "idle" && (
                              <motion.div
                                className={cn("absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full", {
                                  "bg-amber-500": a.status === "analyzing" || a.status === "scanning" || a.status === "negotiating",
                                  "bg-muted-foreground": a.status === "waiting",
                                })}
                                animate={{ scale: [1, 1.3, 1] }}
                                transition={{ duration: 1.5, repeat: Infinity }}
                              />
                            )}
                            {a.status === "complete" && (
                              <CheckCircle2 className="absolute -top-1 -right-1 h-2.5 w-2.5 text-emerald-500" />
                            )}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="text-xs font-medium">{meta.label}</div>
                            <div className="text-[11px] text-muted-foreground leading-relaxed">{a.message}</div>
                            {a.progress !== undefined && a.progress > 0 && a.progress < 100 && (
                              <div className="mt-1.5 h-1 rounded-full bg-muted overflow-hidden">
                                <motion.div
                                  className="h-full rounded-full bg-primary"
                                  initial={{ width: 0 }}
                                  animate={{ width: `${a.progress}%` }}
                                  transition={{ duration: 1, delay: 0.5 }}
                                />
                              </div>
                            )}
                          </div>
                        </motion.div>
                      );
                    })
                  )}
                </div>
              </Card>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
              <Card className="p-5">
                <h3 className="text-sm font-semibold mb-3">Quick Stats</h3>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { label: "This Week", value: meetings?.length || "0", sub: "meetings" },
                    { label: "Connected", value: "1", sub: "calendar" },
                    { label: "Ready", value: "✓", sub: "to schedule" },
                    { label: "AI Agents", value: "4", sub: "active" },
                  ].map((stat) => (
                    <div key={stat.label} className="text-center p-3 rounded-lg bg-muted/50">
                      <div className="text-xl font-bold text-primary tabular-nums">{stat.value}</div>
                      <div className="text-[10px] text-muted-foreground">{stat.label}</div>
                    </div>
                  ))}
                </div>
              </Card>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}

function SlotCard({ slot, index, onSelect }: { slot: TimeSlot; index: number; onSelect?: (slot: TimeSlot) => void }) {
  const [isBooking, setIsBooking] = useState(false);
  
  console.log(`Slot ${index} score:`, slot.score, "Full slot:", slot);
  
  const handleBook = async () => {
    if (!onSelect) return;
    setIsBooking(true);
    try {
      await onSelect(slot);
    } finally {
      setIsBooking(false);
    }
  };
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08 }}
    >
      <Card
        className={cn(
          "p-4 transition-all hover:border-primary/30 cursor-pointer",
          slot.recommended && "border-primary/40 bg-primary/5"
        )}
        data-testid={`card-slot-${slot.id}`}
      >
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm font-semibold">
                {formatDate(slot.start_time)} · {formatTime(slot.start_time)} — {formatTime(slot.end_time)}
              </span>
              {slot.recommended && (
                <Badge className="text-[10px] px-1.5 py-0 bg-primary/20 text-primary border-0">
                  <Star className="h-2.5 w-2.5 mr-0.5" />
                  Best
                </Badge>
              )}
              {slot.requiresApproval && (
                <Badge variant="secondary" className="text-[10px] px-1.5 py-0 bg-amber-500/10 text-amber-600 dark:text-amber-400 border-0">
                  <AlertTriangle className="h-2.5 w-2.5 mr-0.5" />
                  Approval
                </Badge>
              )}
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed">{slot.reasoning}</p>
            {slot.conflicts.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1.5">
                {slot.conflicts.map((c, ci) => (
                  <span key={ci} className={cn(
                    "text-[10px] px-2 py-0.5 rounded-full",
                    c.type === "soft" ? "bg-amber-500/10 text-amber-600 dark:text-amber-400" : "bg-red-500/10 text-red-600 dark:text-red-400"
                  )}>
                    {c.type === "soft" ? <AlertTriangle className="h-2.5 w-2.5 inline mr-0.5" /> : <XCircle className="h-2.5 w-2.5 inline mr-0.5" />}
                    {c.description}
                  </span>
                ))}
              </div>
            )}
            <div className="mt-3">
              <Button 
                size="sm" 
                onClick={handleBook}
                disabled={isBooking}
                className="text-xs"
              >
                {isBooking ? "Booking..." : "Book This Slot"}
              </Button>
            </div>
          </div>
          <div className="text-right shrink-0">
            <div className={cn(
              "text-2xl font-bold tabular-nums",
              slot.score >= 90 ? "text-emerald-500" : slot.score >= 70 ? "text-amber-500" : "text-muted-foreground"
            )}>
              {Math.round(slot.score)}
            </div>
            <div className="text-[10px] text-muted-foreground">score</div>
          </div>
        </div>
      </Card>
    </motion.div>
  );
}
