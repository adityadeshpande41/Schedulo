import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface ScheduloAssistantProps {
  size?: "sm" | "md" | "lg" | "xl";
  animate?: boolean;
  className?: string;
  glowing?: boolean;
}

const sizeMap = {
  sm: 32,
  md: 48,
  lg: 72,
  xl: 120,
};

export function ScheduloAssistant({ size = "md", animate = true, className, glowing = false }: ScheduloAssistantProps) {
  const s = sizeMap[size];

  return (
    <motion.div
      className={cn("relative inline-flex items-center justify-center", className)}
      style={{ width: s, height: s }}
      animate={animate ? { y: [0, -4, 0] } : undefined}
      transition={animate ? { duration: 3, repeat: Infinity, ease: "easeInOut" } : undefined}
    >
      {glowing && (
        <motion.div
          className="absolute inset-0 rounded-full bg-primary/20 blur-xl"
          animate={{ scale: [1, 1.3, 1], opacity: [0.3, 0.6, 0.3] }}
          transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
        />
      )}
      <svg viewBox="0 0 120 120" fill="none" className="w-full h-full relative z-10">
        <defs>
          <linearGradient id="schedulo-grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="hsl(217, 91%, 60%)" />
            <stop offset="50%" stopColor="hsl(250, 80%, 65%)" />
            <stop offset="100%" stopColor="hsl(280, 70%, 60%)" />
          </linearGradient>
          <linearGradient id="schedulo-inner" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="hsl(217, 91%, 70%)" />
            <stop offset="100%" stopColor="hsl(260, 80%, 75%)" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="2" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        
        {/* Alarm bells on top (external hands) */}
        <AlarmBells animate={animate} />
        
        {/* Main clock body */}
        <circle cx="60" cy="60" r="52" fill="url(#schedulo-grad)" opacity="0.15" />
        <circle cx="60" cy="60" r="40" fill="url(#schedulo-grad)" />
        {animate ? (
          <motion.circle
            cx="60" cy="60" r={42}
            stroke="url(#schedulo-inner)"
            strokeWidth="2"
            fill="none"
            opacity={0.6}
            style={{ transformOrigin: "60px 60px" }}
            animate={{ scale: [0.95, 1.05, 0.95] }}
            transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
          />
        ) : (
          <circle
            cx="60" cy="60" r="42"
            stroke="url(#schedulo-inner)"
            strokeWidth="2"
            fill="none"
            opacity={0.6}
          />
        )}
        
        {/* Smiley face */}
        <EyeGroup animate={animate} />
        <motion.path
          d="M 46 70 Q 60 80 74 70"
          stroke="white"
          strokeWidth="2.5"
          strokeLinecap="round"
          fill="none"
          filter="url(#glow)"
        />
        
        {/* Legs at the bottom */}
        <ClockLegs animate={animate} />
      </svg>
    </motion.div>
  );
}

function EyeGroup({ animate }: { animate: boolean }) {
  return (
    <g>
      <ellipse cx="45" cy="55" rx="7" ry="8" fill="white" />
      <ellipse cx="75" cy="55" rx="7" ry="8" fill="white" />
      <motion.ellipse
        cx="46" cy="56" rx="4" ry="4.5"
        fill="hsl(220, 80%, 25%)"
        animate={animate ? { cy: [56, 54, 56] } : undefined}
        transition={animate ? { duration: 3.5, repeat: Infinity, ease: "easeInOut" } : undefined}
      />
      <motion.ellipse
        cx="76" cy="56" rx="4" ry="4.5"
        fill="hsl(220, 80%, 25%)"
        animate={animate ? { cy: [56, 54, 56] } : undefined}
        transition={animate ? { duration: 3.5, repeat: Infinity, ease: "easeInOut" } : undefined}
      />
      <circle cx="43" cy="53" r="2" fill="white" opacity="0.8" />
      <circle cx="73" cy="53" r="2" fill="white" opacity="0.8" />
      {animate && (
        <motion.rect
          x="38" y="47" width="14" height="16" rx="7" fill="url(#schedulo-grad)"
          initial={{ scaleY: 0 }}
          style={{ transformOrigin: "45px 47px" }}
          animate={{ scaleY: [0, 1, 1, 0] }}
          transition={{ duration: 0.3, repeat: Infinity, repeatDelay: 4, times: [0, 0.15, 0.85, 1] }}
        />
      )}
      {animate && (
        <motion.rect
          x="68" y="47" width="14" height="16" rx="7" fill="url(#schedulo-grad)"
          initial={{ scaleY: 0 }}
          style={{ transformOrigin: "75px 47px" }}
          animate={{ scaleY: [0, 1, 1, 0] }}
          transition={{ duration: 0.3, repeat: Infinity, repeatDelay: 4, times: [0, 0.15, 0.85, 1] }}
        />
      )}
    </g>
  );
}

function AlarmBells({ animate }: { animate: boolean }) {
  return (
    <g>
      {/* Left bell */}
      <motion.g
        animate={animate ? { rotate: [-8, 8, -8] } : undefined}
        style={{ transformOrigin: "35px 18px" }}
        transition={animate ? { duration: 0.6, repeat: Infinity, repeatDelay: 2.5 } : undefined}
      >
        <path
          d="M 30 18 L 25 12"
          stroke="hsl(280, 70%, 70%)"
          strokeWidth="3"
          strokeLinecap="round"
        />
        <circle cx="30" cy="18" r="5" fill="hsl(280, 70%, 70%)" />
      </motion.g>
      
      {/* Right bell */}
      <motion.g
        animate={animate ? { rotate: [8, -8, 8] } : undefined}
        style={{ transformOrigin: "85px 18px" }}
        transition={animate ? { duration: 0.6, repeat: Infinity, repeatDelay: 2.5 } : undefined}
      >
        <path
          d="M 90 18 L 95 12"
          stroke="hsl(280, 70%, 70%)"
          strokeWidth="3"
          strokeLinecap="round"
        />
        <circle cx="90" cy="18" r="5" fill="hsl(280, 70%, 70%)" />
      </motion.g>
      
      {/* Top button/knob */}
      <circle cx="60" cy="12" r="4" fill="hsl(280, 70%, 70%)" />
    </g>
  );
}

function ClockLegs({ animate }: { animate: boolean }) {
  return (
    <g>
      {/* Left leg */}
      <motion.g
        animate={animate ? { rotate: [-3, 3, -3] } : undefined}
        style={{ transformOrigin: "45px 102px" }}
        transition={animate ? { duration: 3, repeat: Infinity, ease: "easeInOut" } : undefined}
      >
        <line
          x1="45" y1="102"
          x2="40" y2="115"
          stroke="hsl(280, 70%, 70%)"
          strokeWidth="3"
          strokeLinecap="round"
        />
        <circle cx="40" cy="115" r="4" fill="hsl(280, 70%, 70%)" />
      </motion.g>
      
      {/* Right leg */}
      <motion.g
        animate={animate ? { rotate: [3, -3, 3] } : undefined}
        style={{ transformOrigin: "75px 102px" }}
        transition={animate ? { duration: 3, repeat: Infinity, ease: "easeInOut" } : undefined}
      >
        <line
          x1="75" y1="102"
          x2="80" y2="115"
          stroke="hsl(280, 70%, 70%)"
          strokeWidth="3"
          strokeLinecap="round"
        />
        <circle cx="80" cy="115" r="4" fill="hsl(280, 70%, 70%)" />
      </motion.g>
    </g>
  );
}
