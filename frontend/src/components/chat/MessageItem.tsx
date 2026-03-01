"use client";

import { cn } from "@/lib/utils";
import { Message } from "@/lib/types";
import { formatDuration, formatTimestamp } from "@/lib/utils";
import { LoadingDots } from "@/components/common/LoadingDots";
import { AgentEvents } from "@/components/agent/AgentEvents";
import { DiffViewer } from "@/components/agent/DiffViewer";
import { MarkdownRenderer } from "@/components/chat/MarkdownRenderer";
import { Bot, User, AlertCircle, CheckCircle, Loader2 } from "lucide-react";

interface MessageItemProps {
  message: Message;
}

export function MessageItem({ message }: MessageItemProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex gap-4 p-4 animate-fade-in",
        isUser ? "bg-background" : "bg-card"
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0",
          isUser ? "bg-muted" : "bg-primary/20"
        )}
      >
        {isUser ? (
          <User className="w-5 h-5" />
        ) : (
          <Bot className="w-5 h-5 text-primary" />
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        {/* Header */}
        <div className="flex items-center gap-2 mb-2">
          <span className="font-medium">
            {isUser ? "You" : "OpenCoder"}
          </span>
          {!isUser && message.model && (
            <span className="text-xs text-muted-foreground">
              • {message.model}
            </span>
          )}
          <span className="text-xs text-muted-foreground">
            {formatTimestamp(message.timestamp)}
          </span>
          {message.duration && (
            <span className="text-xs text-muted-foreground">
              • {formatDuration(message.duration)}
            </span>
          )}
          
          {/* Status indicator */}
          {message.status === "processing" && (
            <span className="flex items-center gap-1 text-xs text-muted-foreground">
              <Loader2 className="w-3 h-3 animate-spin" />
              Processing
            </span>
          )}
          {message.status === "error" && (
            <span className="flex items-center gap-1 text-xs text-red-500">
              <AlertCircle className="w-3 h-3" />
              Error
            </span>
          )}
          {message.status === "success" && !isUser && (
            <span className="flex items-center gap-1 text-xs text-green-500">
              <CheckCircle className="w-3 h-3" />
              Complete
            </span>
          )}
        </div>

        {/* User message content */}
        {isUser ? (
          <MarkdownRenderer content={message.content} />
        ) : (
          <div className="space-y-4">
            {/* Error message */}
            {message.error && (
              <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-md text-sm text-red-500">
                <AlertCircle className="w-4 h-4 inline mr-2" />
                {message.error}
              </div>
            )}

            {/* Agent events (thinking, planning, editing, etc.) */}
            {message.events && message.events.length > 0 && (
              <AgentEvents events={message.events} />
            )}

            {/* Main response content */}
            {message.content && (
              <MarkdownRenderer content={message.content} />
            )}

            {/* File changes summary */}
            {message.fileChanges && message.fileChanges.length > 0 && (
              <div className="space-y-2">
                <div className="text-sm font-medium">Files changed:</div>
                <ul className="space-y-1">
                  {message.fileChanges.map((file, idx) => (
                    <li
                      key={`${file.filename}-${idx}`}
                      className="text-xs font-mono text-muted-foreground"
                    >
                      <span
                        className={cn(
                          "mr-2",
                          file.operation === "created" && "text-green-500",
                          file.operation === "modified" && "text-yellow-500",
                          file.operation === "deleted" && "text-red-500"
                        )}
                      >
                        [{file.operation?.charAt(0).toUpperCase() || "M"}]</span>
                      {file.filename}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Diff viewer */}
            {message.diffs && <DiffViewer diffs={message.diffs} />}
          </div>
        )}
      </div>
    </div>
  );
}
