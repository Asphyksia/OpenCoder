import { cn } from "@/lib/utils";
import { AgentStatus } from "@/lib/types";

interface StatusBadgeProps {
  status: AgentStatus;
  className?: string;
  showLabel?: boolean;
}

const statusConfig = {
  ready: {
    label: "Ready",
    color: "bg-green-500",
    textColor: "text-green-500",
    borderColor: "border-green-500/30",
  },
  busy: {
    label: "Busy",
    color: "bg-yellow-500",
    textColor: "text-yellow-500",
    borderColor: "border-yellow-500/30",
  },
  error: {
    label: "Error",
    color: "bg-red-500",
    textColor: "text-red-500",
    borderColor: "border-red-500/30",
  },
  no_session: {
    label: "No Session",
    color: "bg-gray-500",
    textColor: "text-gray-500",
    borderColor: "border-gray-500/30",
  },
};

export function StatusBadge({ status, className, showLabel = true }: StatusBadgeProps) {
  const config = statusConfig[status];

  return (
    <div className={cn("flex items-center gap-2", className)}>
      <div
        className={cn(
          "w-2.5 h-2.5 rounded-full animate-pulse",
          config.color
        )}
      />
      {showLabel && (
        <span className={cn("text-sm font-medium", config.textColor)}>
          {config.label}
        </span>
      )}
    </div>
  );
}
