"use client";

import { AgentEvent, EventType } from "@/lib/types";
import { cn } from "@/lib/utils";
import {
  Brain,
  ClipboardList,
  Pencil,
  FileText,
  GitBranch,
  AlertCircle,
  Settings,
  CheckCircle,
  Loader2,
  MessageSquare,
} from "lucide-react";

interface AgentEventsProps {
  events: AgentEvent[];
}

const defaultConfig = {
  icon: MessageSquare,
  color: "text-gray-400",
  label: "Unknown",
};

const eventConfig: Record<
  EventType,
  { icon: typeof Brain; color: string; label: string }
> = {
  thinking: {
    icon: Brain,
    color: "text-gray-400",
    label: "Thinking",
  },
  planning: {
    icon: ClipboardList,
    color: "text-blue-400",
    label: "Planning",
  },
  editing: {
    icon: Pencil,
    color: "text-green-400",
    label: "Editing",
  },
  file: {
    icon: FileText,
    color: "text-cyan-400",
    label: "File",
  },
  git: {
    icon: GitBranch,
    color: "text-orange-400",
    label: "Git",
  },
  error: {
    icon: AlertCircle,
    color: "text-red-400",
    label: "Error",
  },
  system: {
    icon: Settings,
    color: "text-gray-400",
    label: "System",
  },
  complete: {
    icon: CheckCircle,
    color: "text-green-400",
    label: "Complete",
  },
};

export function AgentEvents({ events }: AgentEventsProps) {
  return (
    <div className="space-y-2">
      {events.map((event, idx) => {
        const config = eventConfig[event.event_type] || defaultConfig;
        const Icon = config.icon;

        return (
          <div
            key={`${event.event_type}-${idx}`}
            className={cn(
              "flex items-start gap-2 p-2 rounded-md bg-muted/50 animate-fade-in"
            )}
            style={{ animationDelay: `${idx * 100}ms` }}
          >
            <Icon className={cn("w-4 h-4 mt-0.5 flex-shrink-0", config.color)} />
            <div className="flex-1 min-w-0">
              <span className={cn("text-xs font-medium", config.color)}>
                {config.label}
              </span>
              <p className="text-xs text-muted-foreground whitespace-pre-wrap">
                {event.content}
              </p>
            </div>
            {event.event_type === "thinking" && idx === events.length - 1 && (
              <Loader2 className={cn("w-3 h-3 animate-spin", config.color)} />
            )}
          </div>
        );
      })}
    </div>
  );
}
