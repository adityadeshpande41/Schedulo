import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Navbar } from "@/components/schedulo/navbar";
import { useTheme } from "@/hooks/use-theme";
import Landing from "@/pages/landing";
import Dashboard from "@/pages/dashboard";
import AgentFlow from "@/pages/agent-flow";
import DecisionPage from "@/pages/decision";
import TryDemo from "@/pages/try-demo";
import LearnMore from "@/pages/learn-more";
import NotFound from "@/pages/not-found";

function Router() {
  const { theme, toggleTheme } = useTheme();

  return (
    <>
      <Switch>
        <Route path="/">
          {() => (
            <>
              <Navbar theme={theme} onToggleTheme={toggleTheme} variant="landing" />
              <Landing />
            </>
          )}
        </Route>
        <Route path="/dashboard">
          {() => (
            <>
              <Navbar theme={theme} onToggleTheme={toggleTheme} variant="app" />
              <Dashboard />
            </>
          )}
        </Route>
        <Route path="/agents">
          {() => (
            <>
              <Navbar theme={theme} onToggleTheme={toggleTheme} variant="app" />
              <AgentFlow />
            </>
          )}
        </Route>
        <Route path="/decision">
          {() => (
            <>
              <Navbar theme={theme} onToggleTheme={toggleTheme} variant="app" />
              <DecisionPage />
            </>
          )}
        </Route>
        <Route path="/try-demo">
          {() => (
            <>
              <Navbar theme={theme} onToggleTheme={toggleTheme} variant="landing" />
              <TryDemo />
            </>
          )}
        </Route>
        <Route path="/learn-more">
          {() => (
            <>
              <Navbar theme={theme} onToggleTheme={toggleTheme} variant="landing" />
              <LearnMore />
            </>
          )}
        </Route>
        <Route component={NotFound} />
      </Switch>
    </>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Router />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
