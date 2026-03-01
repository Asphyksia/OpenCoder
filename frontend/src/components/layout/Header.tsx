"use client";

import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { StatusBadge } from "@/components/common/StatusBadge";
import { useAppStore } from "@/store/useAppStore";
import { useModels } from "@/hooks/useModels";
import { useStatus } from "@/hooks/useStatus";
import { Model } from "@/lib/types";
import { Sun, Moon, Menu, Settings, MoreVertical, Trash2, Download, Plus } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export function Header() {
  const [mounted, setMounted] = useState(false);
  const [theme, setTheme] = useState<"light" | "dark">("dark");
  const { agentStatus, selectedModel, setSelectedModel, sidebarOpen, setSidebarOpen, settingsOpen, setSettingsOpen, availableModels, clearMessages, messages } = useAppStore();
  const { models, isLoading: modelsLoading } = useModels();
  const { status, isLoading: statusLoading, error: statusError } = useStatus();

  // Get display name for selected model
  const getDisplayName = (modelName: string) => {
    const model = models.find(m => m.name === modelName);
    return model?.display_name || model?.name || modelName;
  };

  useEffect(() => {
    setMounted(true);
    // Check system preference
    if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
      setTheme("dark");
    }
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === "dark" ? "light" : "dark";
    setTheme(newTheme);
    document.documentElement.classList.remove("dark", "light");
    document.documentElement.classList.add(newTheme);
  };

  return (
    <header className="h-14 border-b border-border bg-card flex items-center justify-between px-4">
      <div className="flex items-center gap-4">
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="lg:hidden p-2 hover:bg-muted rounded-md"
          aria-label="Toggle sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div className="flex items-center gap-2">
          <img src="/logo.png" alt="OpenCoder" className="h-8 w-8 rounded-md object-contain bg-white" />
          <span className="text-xl font-bold">OpenCoder</span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        {/* Model Selector */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="flex items-center gap-2 px-3 py-1.5 text-sm rounded-md border border-border hover:bg-muted transition-colors z-50">
              <span>{selectedModel ? getDisplayName(selectedModel) : "Loading..."}</span>
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56 z-[100]">
            {models.length > 0 ? (
              models.map((model: Model, index: number) => (
                <DropdownMenuItem
                  key={`${model.name}-${index}`}
                  onClick={() => setSelectedModel(model.name)}
                  className={cn(
                    selectedModel === model.name && "bg-muted"
                  )}
                >
                  <div className="flex flex-col">
                    <span>{model.display_name || model.name}</span>
                    <span className="text-xs text-muted-foreground">
                      {model.provider} • {model.category || "General"}
                    </span>
                  </div>
                </DropdownMenuItem>
              ))
            ) : (
              <DropdownMenuItem disabled>
                <span className="text-muted-foreground">No models available</span>
              </DropdownMenuItem>
            )}
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 hover:bg-muted rounded-md transition-colors"
          aria-label="Toggle theme"
        >
          {mounted && theme === "dark" ? (
            <Sun className="w-5 h-5" />
          ) : (
            <Moon className="w-5 h-5" />
          )}
        </button>

        {/* Settings */}
        <button
          onClick={() => setSettingsOpen(true)}
          className="p-2 hover:bg-muted rounded-md transition-colors"
          aria-label="Open settings"
        >
          <Settings className="w-5 h-5" />
        </button>

        {/* More Options */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button
              className="p-2 hover:bg-muted rounded-md transition-colors"
              aria-label="More options"
            >
              <MoreVertical className="w-5 h-5" />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48 z-[100]">
            <DropdownMenuItem onClick={clearMessages}>
              <Trash2 className="w-4 h-4 mr-2" />
              Clear chat
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => {
              clearMessages();
              window.location.reload();
            }}>
              <Plus className="w-4 h-4 mr-2" />
              New session
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
