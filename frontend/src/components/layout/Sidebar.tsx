"use client";

import { cn } from "@/lib/utils";
import { useAppStore } from "@/store/useAppStore";
import { useMemo, useState, useEffect } from "react";
import { useStatus } from "@/hooks/useStatus";
import { StatusBadge } from "@/components/common/StatusBadge";
import { Collapsible } from "@/components/common/Collapsible";
import type { FileChange } from "@/lib/types";
import {
  Plus,
  FileText,
  FolderOpen,
  Settings,
  X,
  ChevronRight,
  Clock,
  Folder,
} from "lucide-react";

export function Sidebar() {
  const { 
    sidebarOpen, 
    setSidebarOpen, 
    agentStatus, 
    repoPath, 
    messages,
    clearMessages,
  } = useAppStore();
  const { status } = useStatus();
  const [projectFiles, setProjectFiles] = useState<string[]>([]);

  // Fetch project files
  useEffect(() => {
    async function fetchFiles() {
      try {
        const response = await fetch('http://localhost:8001/files');
        if (response.ok) {
          const data = await response.json();
          setProjectFiles(data.files || []);
        }
      } catch {
        // API not available, use empty
        setProjectFiles([]);
      }
    }
    if (repoPath) {
      fetchFiles();
    }
  }, [repoPath]);

  // Get all file changes from messages
  const fileChanges: FileChange[] = useMemo(() => {
    return messages
      .filter((m) => m.fileChanges && m.fileChanges.length > 0)
      .flatMap((m) => m.fileChanges || [])
      .reduce<FileChange[]>((acc, file) => {
        if (!acc.find((f) => f.filename === file.filename)) {
          acc.push(file);
        }
        return acc;
      }, []);
  }, [messages]);

  const handleNewChat = () => {
    clearMessages();
  };

  if (!sidebarOpen) return null;

  return (
    <>
      {/* Overlay for mobile */}
      <div
        className="fixed inset-0 bg-black/50 z-40 lg:hidden"
        onClick={() => setSidebarOpen(false)}
      />

      <aside
        className={cn(
          "fixed lg:static inset-y-0 left-0 z-50 w-72 bg-card border-r border-border flex flex-col transition-transform duration-200",
          "lg:translate-x-0",
          !sidebarOpen && "-translate-x-full"
        )}
      >
        {/* Header */}
        <div className="h-14 flex items-center justify-between px-4 border-b border-border">
          <h2 className="font-semibold"></h2>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-2 hover:bg-muted rounded-md"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* New Chat Button */}
          <button
            onClick={handleNewChat}
            className="w-full flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span className="font-medium">New Chat</span>
          </button>

          {/* Status Section */}
          <Collapsible title="Status" defaultOpen>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Status</span>
                <StatusBadge status={agentStatus} />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Repository</span>
                <span className="text-xs font-mono truncate max-w-[120px]">
                  {repoPath}
                </span>
              </div>
              {/* Use local file changes count for consistency */}
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Changes</span>
                <span>{fileChanges.length} files</span>
              </div>
            </div>
          </Collapsible>

          {/* Project Files */}
          <Collapsible title="Project Files" defaultOpen>
            <div className="space-y-1">
              {projectFiles.length > 0 ? (
                projectFiles.slice(0, 20).map((file, idx) => (
                  <button
                    key={`${file}-${idx}`}
                    className="w-full flex items-center gap-2 px-2 py-1 text-sm hover:bg-muted rounded text-left"
                  >
                    <FileText className="w-3 h-3 flex-shrink-0 text-muted-foreground" />
                    <span className="truncate font-mono text-xs">{file}</span>
                  </button>
                ))
              ) : (
                <div className="text-xs text-muted-foreground px-2">
                  No files in workspace
                </div>
              )}
              {projectFiles.length > 20 && (
                <div className="text-xs text-muted-foreground px-2">
                  +{projectFiles.length - 20} more files
                </div>
              )}
            </div>
          </Collapsible>

          {/* Modified Files (from current session) */}
          {fileChanges.length > 0 && (
            <Collapsible title="Modified in Session" defaultOpen>
              <ul className="space-y-1 text-sm">
                {fileChanges.map((file, idx) => (
                  <li
                    key={`${file.filename}-${idx}`}
                    className="flex items-center gap-2 truncate"
                  >
                    <FileText className="w-3 h-3 flex-shrink-0" />
                    <span className="truncate font-mono text-xs">
                      {file.filename}
                    </span>
                    <span className="text-xs text-muted-foreground ml-auto">
                      {file.operation}
                    </span>
                  </li>
                ))}
              </ul>
            </Collapsible>
          )}

          {/* Settings */}
          <Collapsible title="Settings">
            <div className="space-y-2 text-sm">
              <button className="w-full flex items-center gap-2 px-2 py-1 hover:bg-muted rounded text-left">
                <FolderOpen className="w-3 h-3" />
                <span className="text-xs">Workspace Path</span>
              </button>
            </div>
          </Collapsible>
        </div>
      </aside>
    </>
  );
}
