"use client";

import { cn } from "@/lib/utils";
import { useAppStore } from "@/store/useAppStore";
import { useMemo } from "react";
import { useModels } from "@/hooks/useModels";
import { useStatus } from "@/hooks/useStatus";
import { StatusBadge } from "@/components/common/StatusBadge";
import { Collapsible } from "@/components/common/Collapsible";
import type { FileChange } from "@/lib/types";
import {
  FileText,
  GitBranch,
  Cpu,
  FolderOpen,
  X,
} from "lucide-react";

export function Sidebar() {
  const { sidebarOpen, setSidebarOpen, agentStatus, repoPath, messages } = useAppStore();
  const { models } = useModels();
  const { status } = useStatus();

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
          <h2 className="font-semibold">Session Status</h2>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-2 hover:bg-muted rounded-md"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Status Section */}
          <Collapsible title="Status" defaultOpen>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Status</span>
                <StatusBadge status={agentStatus} />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Model</span>
                <span className="text-xs">
                  {useAppStore.getState().selectedModel}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Repository</span>
                <span className="text-xs font-mono truncate max-w-[120px]">
                  {repoPath}
                </span>
              </div>
              {status && (
                <>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Events</span>
                    <span>{status.events_count}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Changes</span>
                    <span>{status.file_changes_count} files</span>
                  </div>
                </>
              )}
            </div>
          </Collapsible>

          {/* Modified Files */}
          {fileChanges.length > 0 && (
            <Collapsible title="Modified Files" defaultOpen>
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

          {/* Available Models */}
          <Collapsible title="Available Models" defaultOpen>
            <ul className="space-y-1 text-sm">
              {models.map((model, index) => (
                <li
                  key={`${model.name}-${index}`}
                  className="flex items-center gap-2 truncate"
                >
                  <Cpu className="w-3 h-3 flex-shrink-0" />
                  <span className="truncate text-xs">{model.name}</span>
                  <span className="text-xs text-muted-foreground ml-auto">
                    {model.category}
                  </span>
                </li>
              ))}
              {models.length === 0 && (
                <li className="text-muted-foreground text-xs">
                  No models available
                </li>
              )}
            </ul>
          </Collapsible>
        </div>
      </aside>
    </>
  );
}
