"use client";

import { useState, useRef, useEffect, KeyboardEvent, useCallback } from "react";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/store/useAppStore";
import type { Attachment, SlashCommand } from "@/lib/types";
import {
  Send,
  Loader2,
  Lock,
  Paperclip,
  X,
  FileText,
  Image,
  ChevronDown,
  Hash,
} from "lucide-react";

// Available slash commands
const SLASH_COMMANDS: SlashCommand[] = [
  { name: "/new", description: "Start a new conversation", action: "new" },
  { name: "/clear", description: "Clear current chat", action: "clear" },
  { name: "/model", description: "Change AI model", action: "model" },
  { name: "/help", description: "Show available commands", action: "help" },
  { name: "/files", description: "Show project files", action: "files" },
  { name: "/read-only", description: "Toggle read-only mode", action: "toggle-readonly" },
];

interface MessageInputProps {
  onSend: (message: string, attachments?: Attachment[]) => void;
  isProcessing?: boolean;
}

export function MessageInput({ onSend, isProcessing = false }: MessageInputProps) {
  const [message, setMessage] = useState("");
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [showCommands, setShowCommands] = useState(false);
  const [filteredCommands, setFilteredCommands] = useState<SlashCommand[]>(SLASH_COMMANDS);
  const [selectedCommandIndex, setSelectedCommandIndex] = useState(0);
  const [isDragOver, setIsDragOver] = useState(false);
  
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const commandsRef = useRef<HTMLDivElement>(null);
  
  const { 
    selectedModel, 
    setSelectedModel, 
    readOnly, 
    setReadOnly, 
    clearMessages,
    setSidebarOpen,
  } = useAppStore();

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [message]);

  // Filter commands based on input
  useEffect(() => {
    if (message.startsWith("/")) {
      const filtered = SLASH_COMMANDS.filter(cmd => 
        cmd.name.toLowerCase().includes(message.toLowerCase())
      );
      setFilteredCommands(filtered);
      setShowCommands(filtered.length > 0);
      setSelectedCommandIndex(0);
    } else {
      setShowCommands(false);
    }
  }, [message]);

  // Close commands when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (commandsRef.current && !commandsRef.current.contains(event.target as Node)) {
        setShowCommands(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      // Ctrl/Cmd + N: New chat
      if ((e.ctrlKey || e.metaKey) && e.key === "n") {
        e.preventDefault();
        handleCommand("new");
      }
      // Ctrl/Cmd + K: Clear chat
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        handleCommand("clear");
      }
      // Ctrl/Cmd + /: Toggle sidebar
      if ((e.ctrlKey || e.metaKey) && e.key === "/") {
        e.preventDefault();
        const current = useAppStore.getState().sidebarOpen;
        setSidebarOpen(!current);
      }
    }
    
    const element = textareaRef.current;
    if (element) {
      element.addEventListener("keydown", handleKeyDown as any);
      return () => element.removeEventListener("keydown", handleKeyDown as any);
    }
  }, [setSidebarOpen]);

  const handleSend = () => {
    if (!message.trim() || isProcessing) return;
    onSend(message.trim(), attachments.length > 0 ? attachments : undefined);
    setMessage("");
    setAttachments([]);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Command palette navigation
    if (showCommands) {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedCommandIndex(prev => Math.min(prev + 1, filteredCommands.length - 1));
        return;
      }
      if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedCommandIndex(prev => Math.max(prev - 1, 0));
        return;
      }
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        if (filteredCommands[selectedCommandIndex]) {
          handleCommand(filteredCommands[selectedCommandIndex].action);
          return;
        }
      }
      if (e.key === "Escape") {
        setShowCommands(false);
        return;
      }
    }
    
    // Send message
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleCommand = (action: string) => {
    switch (action) {
      case "new":
        clearMessages();
        setMessage("");
        break;
      case "clear":
        clearMessages();
        break;
      case "model":
        // Toggle through models (simple implementation)
        setMessage("");
        break;
      case "help":
        setMessage("Available commands:\n" + SLASH_COMMANDS.map(c => `${c.name} - ${c.description}`).join("\n"));
        break;
      case "files":
        setSidebarOpen(true);
        setMessage("");
        break;
      case "toggle-readonly":
        setReadOnly(!readOnly);
        setMessage("");
        break;
      default:
        break;
    }
    setShowCommands(false);
  };

  // File handling
  const handleFileSelect = async (files: FileList | null) => {
    if (!files) return;
    
    const newAttachments: Attachment[] = [];
    
    for (const file of Array.from(files)) {
      // Skip if too large (> 1MB)
      if (file.size > 1024 * 1024) {
        alert(`File ${file.name} is too large. Maximum size is 1MB.`);
        continue;
      }
      
      const attachment: Attachment = {
        id: Math.random().toString(36).substring(2, 9),
        name: file.name,
        size: file.size,
        type: file.type,
      };
      
      // Read text files
      if (file.type.startsWith("text/") || file.name.match(/\.(py|js|ts|tsx|json|md|txt)$/i)) {
        const content = await file.text();
        attachment.content = content;
      }
      
      newAttachments.push(attachment);
    }
    
    setAttachments(prev => [...prev, ...newAttachments]);
  };

  const removeAttachment = (id: string) => {
    setAttachments(prev => prev.filter(a => a.id !== id));
  };

  // Drag and drop
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    handleFileSelect(e.dataTransfer.files);
  }, []);

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getFileIcon = (type: string) => {
    if (type.startsWith("image/")) return <Image className="w-4 h-4" />;
    return <FileText className="w-4 h-4" />;
  };

  return (
    <div 
      className={cn(
        "border-t border-border bg-card p-4 transition-colors",
        isDragOver && "bg-primary/5 border-primary"
      )}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <div className="max-w-4xl mx-auto">
        {/* Attachments */}
        {attachments.length > 0 && (
          <div className="mb-2 flex flex-wrap gap-2">
            {attachments.map(attachment => (
              <div
                key={attachment.id}
                className="flex items-center gap-2 px-3 py-1.5 bg-muted rounded-md text-sm"
              >
                {getFileIcon(attachment.type)}
                <span className="max-w-[150px] truncate">{attachment.name}</span>
                <span className="text-xs text-muted-foreground">
                  {formatFileSize(attachment.size)}
                </span>
                <button
                  onClick={() => removeAttachment(attachment.id)}
                  className="p-0.5 hover:bg-muted-foreground/20 rounded"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Input container */}
        <div className="relative border border-border rounded-lg bg-background focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2 focus-within:ring-offset-background transition-shadow">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message, / for commands..."
            className="w-full min-h-[60px] max-h-[200px] p-3 pr-24 bg-transparent resize-none focus:outline-none"
            disabled={isProcessing}
            rows={1}
          />

          {/* Slash commands dropdown */}
          {showCommands && filteredCommands.length > 0 && (
            <div
              ref={commandsRef}
              className="absolute bottom-full left-0 right-0 mb-2 bg-popover border border-border rounded-lg shadow-lg overflow-hidden z-10"
            >
              {filteredCommands.map((cmd, index) => (
                <button
                  key={cmd.name}
                  onClick={() => handleCommand(cmd.action)}
                  className={cn(
                    "w-full px-4 py-2 text-left flex items-center gap-3 hover:bg-muted",
                    index === selectedCommandIndex && "bg-muted"
                  )}
                >
                  <Hash className="w-4 h-4 text-muted-foreground" />
                  <div>
                    <div className="font-mono text-sm">{cmd.name}</div>
                    <div className="text-xs text-muted-foreground">{cmd.description}</div>
                  </div>
                </button>
              ))}
            </div>
          )}

          {/* Toolbar */}
          <div className="absolute bottom-2 right-2 flex items-center gap-2">
            {/* Attach button */}
            <button
              onClick={() => fileInputRef.current?.click()}
              className="p-2 hover:bg-muted rounded-md transition-colors text-muted-foreground"
              aria-label="Attach file"
              disabled={isProcessing}
            >
              <Paperclip className="w-4 h-4" />
            </button>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              className="hidden"
              onChange={(e) => handleFileSelect(e.target.files)}
              accept=".py,.js,.ts,.tsx,.json,.md,.txt,.txt,.html,.css,.yaml,.yml,.sh"
            />

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
              disabled={isProcessing}
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

        {/* Keyboard shortcuts hint */}
        <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
          <div className="flex items-center gap-3">
            <span>
              Using: <span className="font-mono">{selectedModel}</span>
            </span>
            <span className="text-muted-foreground/50">|</span>
            <span className="hidden sm:inline">
              <kbd className="px-1 py-0.5 bg-muted rounded text-[10px]">Ctrl</kbd>
              <span className="mx-0.5">+</span>
              <kbd className="px-1 py-0.5 bg-muted rounded text-[10px]">N</kbd>
              <span className="ml-1">New</span>
            </span>
          </div>
          {readOnly && (
            <span className="flex items-center gap-1">
              <Lock className="w-3 h-3" />
              Read-only mode
            </span>
          )}
        </div>
        
        {/* Drag indicator */}
        {isDragOver && (
          <div className="absolute inset-0 flex items-center justify-center bg-primary/10 border-2 border-dashed border-primary rounded-lg pointer-events-none">
            <span className="text-primary font-medium">Drop files here</span>
          </div>
        )}
      </div>
    </div>
  );
}
