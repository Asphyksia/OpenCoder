"use client";

import { useRef, useEffect } from "react";
import { useAppStore } from "@/store/useAppStore";
import { MessageItem } from "./MessageItem";
import { MessageInput } from "./MessageInput";
import { useChat } from "@/hooks/useChat";
import { Message } from "@/lib/types";

export function ChatContainer() {
  const messages = useAppStore((state) => state.messages);
  const scrollRef = useRef<HTMLDivElement>(null);
  const { sendMessage, isProcessing } = useChat();

  // Auto-scroll to bottom when new messages appear
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = (message: string) => {
    sendMessage.mutate(message);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages list */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto"
      >
        {messages.length === 0 ? (
          <EmptyState />
        ) : (
          <div className="divide-y divide-border">
            {messages.map((message) => (
              <MessageItem key={message.id} message={message} />
            ))}
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

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center p-8">
      <div className="w-16 h-16 mb-4 rounded-full bg-primary/20 flex items-center justify-center">
        <svg
          className="w-8 h-8 text-primary"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
          />
        </svg>
      </div>
      <h2 className="text-xl font-semibold mb-2">Start a conversation</h2>
      <p className="text-muted-foreground max-w-md">
        Send a message to start working with the AI agent. Describe what you want to
        build or ask for code changes.
      </p>
      <div className="mt-8 text-sm text-muted-foreground space-y-2">
        <p>Example prompts:</p>
        <ul className="space-y-1">
          <li>• "Create a Python function to calculate fibonacci"</li>
          <li>• "Add error handling to this function"</li>
          <li>• "Refactor this code to use async/await"</li>
        </ul>
      </div>
    </div>
  );
}
