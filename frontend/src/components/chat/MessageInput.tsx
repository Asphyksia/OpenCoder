"use client";

import { useState, useRef, useEffect, KeyboardEvent } from "react";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/store/useAppStore";
import { Send, Loader2, Lock, Paperclip } from "lucide-react";

interface MessageInputProps {
  onSend: (message: string) => void;
  isProcessing?: boolean;
}

export function MessageInput({ onSend, isProcessing = false }: MessageInputProps) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { selectedModel, setSelectedModel, readOnly, setReadOnly, availableModels } = useAppStore();

  useEffect(() => {
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [message]);

  const handleSend = () => {
    if (!message.trim() || isProcessing) return;
    onSend(message.trim());
    setMessage("");
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-border bg-card p-4">
      <div className="max-w-4xl mx-auto">
        <div className="relative border border-border rounded-lg bg-background focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2 focus-within:ring-offset-background transition-shadow">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message or command..."
            className="w-full min-h-[60px] max-h-[200px] p-3 pr-24 bg-transparent resize-none focus:outline-none"
            disabled={isProcessing}
            rows={1}
          />

          {/* Toolbar */}
          <div className="absolute bottom-2 right-2 flex items-center gap-2">
            {/* Attach button (placeholder for future functionality) */}
            <button
              className="p-2 hover:bg-muted rounded-md transition-colors text-muted-foreground"
              aria-label="Attach file"
              disabled
            >
              <Paperclip className="w-4 h-4" />
            </button>

            {/* Read-only toggle */}
            <button
              onClick={() => setReadOnly(!readOnly)}
              className={cn(
                "p-2 rounded-md transition-colors",
                readOnly
                  ? "bg-muted text-foreground"
                  : "hover:bg-muted text-muted-foreground"
              )}
              aria-label={readOnly ? "Disable read-only mode" : "Enable read-only mode"}
            >
              <Lock className="w-4 h-4" />
            </button>

            {/* Send button */}
            <button
              onClick={handleSend}
              disabled={!message.trim() || isProcessing}
              className={cn(
                "p-2 rounded-md transition-colors flex items-center gap-1",
                message.trim() && !isProcessing
                  ? "bg-primary text-primary-foreground hover:bg-primary/90"
                  : "bg-muted text-muted-foreground cursor-not-allowed"
              )}
              aria-label="Send message"
            >
              {isProcessing ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span className="text-sm">Send</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Model info */}
        <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
          <span>
            Using: <span className="font-mono">{selectedModel}</span>
          </span>
          {readOnly && (
            <span className="flex items-center gap-1">
              <Lock className="w-3 h-3" />
              Read-only mode
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
