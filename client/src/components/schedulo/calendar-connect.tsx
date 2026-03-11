import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Calendar, CheckCircle2, Loader2 } from "lucide-react";
import { motion } from "framer-motion";

interface CalendarConnectProps {
  userId: string;
}

export function CalendarConnect({ userId }: CalendarConnectProps) {
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(false);

  useEffect(() => {
    checkCalendarStatus();
  }, [userId]);

  const checkCalendarStatus = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/calendar/status/${userId}`);
      const data = await response.json();
      setConnected(data.connected);
    } catch (error) {
      console.error("Failed to check calendar status:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async () => {
    setConnecting(true);
    try {
      const response = await fetch(`http://localhost:8000/api/calendar/connect/google?user_id=${userId}`);
      const data = await response.json();
      
      // Redirect to Google OAuth
      window.location.href = data.authorization_url;
    } catch (error) {
      console.error("Failed to connect calendar:", error);
      setConnecting(false);
    }
  };

  const handleDisconnect = async () => {
    if (!confirm("Are you sure you want to disconnect your calendar?")) return;
    
    try {
      await fetch(`http://localhost:8000/api/calendar/disconnect/${userId}`, {
        method: "DELETE"
      });
      setConnected(false);
    } catch (error) {
      console.error("Failed to disconnect calendar:", error);
    }
  };

  if (loading) {
    return (
      <Card className="p-5 border-dashed">
        <div className="flex items-center gap-3">
          <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
          <span className="text-sm text-muted-foreground">Checking calendar status...</span>
        </div>
      </Card>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
    >
      <Card className={`p-5 ${connected ? 'border-emerald-500/30 bg-emerald-500/5' : 'border-dashed'}`}>
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-3 flex-1">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
              connected ? 'bg-emerald-500/10' : 'bg-muted'
            }`}>
              {connected ? (
                <CheckCircle2 className="h-5 w-5 text-emerald-600" />
              ) : (
                <Calendar className="h-5 w-5 text-muted-foreground" />
              )}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="text-sm font-semibold">Google Calendar</h3>
                {connected && (
                  <Badge variant="outline" className="text-[10px] border-emerald-500/30 text-emerald-600">
                    Connected
                  </Badge>
                )}
              </div>
              <p className="text-xs text-muted-foreground">
                {connected
                  ? "Your calendar is synced. Schedulo can access your availability."
                  : "Connect your calendar to enable smart scheduling based on your real availability."}
              </p>
            </div>
          </div>
          <div>
            {connected ? (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleDisconnect}
                className="text-xs"
              >
                Disconnect
              </Button>
            ) : (
              <Button
                size="sm"
                onClick={handleConnect}
                disabled={connecting}
                className="text-xs"
              >
                {connecting ? (
                  <>
                    <Loader2 className="h-3 w-3 mr-1.5 animate-spin" />
                    Connecting...
                  </>
                ) : (
                  <>
                    <Calendar className="h-3 w-3 mr-1.5" />
                    Connect
                  </>
                )}
              </Button>
            )}
          </div>
        </div>
      </Card>
    </motion.div>
  );
}
