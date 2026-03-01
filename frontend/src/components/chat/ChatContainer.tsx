"use client";

import { useRef, useEffect, useState } from "react";
import { useAppStore } from "@/store/useAppStore";
import { MessageItem } from "./MessageItem";
import { MessageInput } from "./MessageInput";
import { useChat } from "@/hooks/useChat";
import { useStatus } from "@/hooks/useStatus";
import { useEventStream } from "@/hooks/useEventStream";
import { AgentStatus, Message } from "@/lib/types";
import { 
  Loader2, 
  Sparkles, 
  FileCode, 
  Bug, 
  RefreshCw, 
  BookOpen,
  Zap,
  Clock,
  X,
  Download,
  FileJson,
  FileText,
  Wifi
} from "lucide-react";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

export function ChatContainer() {
  const messages = useAppStore((state) => state.messages);
  const sessionId = useAppStore((state) => state.sessionId);
  const scrollRef = useRef<HTMLDivElement>(null);
  const { sendMessage, isProcessing } = useChat();
  const { status } = useStatus();
  const { events: streamEvents, isConnected } = useEventStream(sessionId);

  // Auto-scroll to bottom when new messages appear
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isProcessing]);

  const handleSend = (message: string) => {
    sendMessage.mutate(message);
  };

  // Export to JSON
  const exportToJson = () => {
    const data = JSON.stringify(messages, null, 2);
    const blob = new Blob([data], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `opencoder-conversation-${new Date().toISOString().split("T")[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("Conversation exported as JSON");
  };

  // Export to Markdown
  const exportToMarkdown = () => {
    let md = "# OpenCoder Conversation\n\n";
    md += `Exported: ${new Date().toISOString()}\n\n`;
    
    messages.forEach((msg) => {
      const role = msg.role === "user" ? "You" : "OpenCoder";
      const time = new Date(msg.timestamp).toLocaleString();
      md += `## ${role} - ${time}\n\n`;
      md += `${msg.content}\n\n`;
      
      if (msg.fileChanges && msg.fileChanges.length > 0) {
        md += "### Files Changed\n\n";
        msg.fileChanges.forEach((file) => {
          md += `- ${file.filename} (${file.operation})\n`;
        });
        md += "\n";
      }
    });
    
    const blob = new Blob([md], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `opencoder-conversation-${new Date().toISOString().split("T")[0]}.md`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("Conversation exported as Markdown");
  };

  return (
    <div className="flex flex-col h-full">
      {/* Export buttons */}
      {messages.length > 0 && (
        <div className="flex items-center gap-2 px-4 py-2 border-b border-border bg-muted/30">
          <span className="text-xs text-muted-foreground">
            {messages.length} messages
          </span>
          <div className="ml-auto flex items-center gap-1">
            <button
              onClick={exportToJson}
              className="flex items-center gap-1 px-2 py-1 text-xs hover:bg-muted rounded transition-colors"
              title="Export as JSON"
            >
              <FileJson className="w-3 h-3" />
              JSON
            </button>
            <button
              onClick={exportToMarkdown}
              className="flex items-center gap-1 px-2 py-1 text-xs hover:bg-muted rounded transition-colors"
              title="Export as Markdown"
            >
              <FileText className="w-3 h-3" />
              MD
            </button>
          </div>
        </div>
      )}

      {/* Messages list */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto"
      >
        {messages.length === 0 ? (
          <EmptyState onSend={handleSend} />
        ) : (
          <div className="divide-y divide-border">
            {messages.map((message) => (
              <MessageItem key={message.id} message={message} />
            ))}
            
            {/* Processing indicator */}
            {isProcessing && (
              <ProcessingIndicator status={status} streamEvents={streamEvents} isConnected={isConnected} />
            )}
          </div>
        )}
      </div>

      {/* Input area */}
      <MessageInput
        onSend={handleSend}
        isProcessing={isProcessing}
      />
    </div>
  );
}

// Quick action buttons
const QUICK_ACTIONS = [
  { label: "Create new file", icon: FileCode, prompt: "Create a new Python file that" },
  { label: "Fix a bug", icon: Bug, prompt: "Find and fix bugs in" },
  { label: "Refactor code", icon: RefreshCw, prompt: "Refactor this code to be cleaner" },
  { label: "Add docs", icon: BookOpen, prompt: "Add documentation to" },
];

interface EmptyStateProps {
  onSend: (message: string) => void;
}

function EmptyState({ onSend }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center p-8">
      {/* Welcome header */}
      <div className="mb-6">
        <div className="w-16 h-16 mb-4 rounded-full bg-primary/20 flex items-center justify-center mx-auto">
          <Sparkles className="w-8 h-8 text-primary" />
        </div>
        <h2 className="text-2xl font-bold mb-2">Welcome to OpenCoder</h2>
        <p className="text-muted-foreground max-w-md">
          Your AI-powered coding assistant powered by Aider + OpenGPU
        </p>
      </div>

      {/* Quick actions */}
      <div className="mb-8 w-full max-w-lg">
        <h3 className="text-sm font-medium mb-3 text-left">🎯 Quick Actions</h3>
        <div className="grid grid-cols-2 gap-2">
          {QUICK_ACTIONS.map((action) => (
            <button
              key={action.label}
              onClick={() => onSend(action.prompt)}
              className="flex items-center gap-2 px-4 py-3 bg-muted hover:bg-muted/80 rounded-lg text-left transition-colors"
            >
              <action.icon className="w-4 h-4 text-primary" />
              <span className="text-sm">{action.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Example prompts */}
      <div className="w-full max-w-lg">
        <h3 className="text-sm font-medium mb-3 text-left">💡 Try asking:</h3>
        <div className="space-y-2 text-left">
          {[
            "Create a FastAPI endpoint for user management",
            "Add unit tests for main.py",
            "Explain this code and suggest improvements",
          ].map((prompt, idx) => (
            <button
              key={idx}
              onClick={() => onSend(prompt)}
              className="w-full px-4 py-2 text-sm text-muted-foreground hover:text-foreground hover:bg-muted rounded-md text-left transition-colors"
            >
              "{prompt}"
            </button>
          ))}
        </div>
      </div>

      {/* Status info */}
      <div className="mt-8 flex items-center gap-4 text-xs text-muted-foreground">
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-green-500"></span>
          Connected to OpenGPU
        </span>
        <span>Model: Qwen/Qwen3-Coder</span>
      </div>
    </div>
  );
}

// Processing indicator component
function ProcessingIndicator({ status, streamEvents, isConnected }: { status: any; streamEvents: any[]; isConnected: boolean }) {
  const [elapsed, setElapsed] = useState(0);
  const agentStatus = useAppStore((state) => state.agentStatus);
  const { clearMessages } = useAppStore();

  // Track elapsed time
  useEffect(() => {
    const interval = setInterval(() => {
      setElapsed(prev => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Get latest stream event
  const latestEvent = streamEvents.length > 0 ? streamEvents[streamEvents.length - 1] : null;

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Determine current step based on status and stream events
  const getCurrentStep = () => {
    // Use stream events if available
    if (latestEvent) {
      return {
        step: latestEvent.message || "Processing...",
        details: isConnected ? "Streaming connected" : "Connecting..."
      };
    }
    
    if (agentStatus === "processing") {
      return {
        step: "Processing your request...",
        details: status?.events_count 
          ? `Events processed: ${status.events_count}`
          : "Analyzing your request"
      };
    }
    return {
      step: "Initializing...",
      details: "Setting up agent session"
    };
  };

  const { step, details } = getCurrentStep();

  return (
    <div className="p-4 border-b border-border bg-card">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-start gap-4">
          {/* Avatar */}
          <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
            <Loader2 className="w-4 h-4 text-primary animate-spin" />
          </div>
          
          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-medium">OpenCoder</span>
              <span className="text-xs px-2 py-0.5 bg-primary/20 text-primary rounded-full">
                Processing
              </span>
              {/* Streaming indicator */}
              {isConnected && (
                <span className="flex items-center gap-1 text-xs text-green-500" title="Streaming connected">
                  <Wifi className="w-3 h-3" />
                  Live
                </span>
              )}
              <div className="ml-auto flex items-center gap-2">
                <Clock className="w-3 h-3 text-muted-foreground" />
                <span className="text-xs text-muted-foreground">{formatTime(elapsed)}</span>
              </div>
            </div>

            {/* Progress bar */}
            <div className="mb-3">
              <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                <div 
                  className="h-full bg-primary rounded-full animate-pulse"
                  style={{ width: '60%' }}
                />
              </div>
            </div>

            {/* Step details */}
            <div className="space-y-1 text-sm">
              <div className="flex items-center gap-2">
                <Zap className="w-3 h-3 text-primary" />
                <span>{step}</span>
              </div>
              <div className="text-xs text-muted-foreground pl-5">
                {details}
              </div>
            </div>

            {/* Events if available */}
            {status?.events_count > 0 && (
              <div className="mt-2 text-xs text-muted-foreground">
                {status.events_count} events processed • {status.file_changes_count || 0} files changed
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
