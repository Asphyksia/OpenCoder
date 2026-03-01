"use client";

import { useAppStore } from "@/store/useAppStore";
import { useModels } from "@/hooks/useModels";
import { X, Settings, Thermometer, FileText, MessageSquare, RotateCcw, Check } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

export function SettingsDialog() {
  const { 
    settingsOpen, 
    setSettingsOpen,
    selectedModel,
    setSelectedModel,
    temperature,
    setTemperature,
    maxTokens,
    setMaxTokens,
    systemPrompt,
    setSystemPrompt,
    availableModels,
  } = useAppStore();
  
  const { models } = useModels();
  const [saved, setSaved] = useState(false);
  
  // Use models from store if available, otherwise use hook
  const modelList = availableModels.length > 0 
    ? availableModels 
    : models;

  if (!settingsOpen) return null;

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleReset = () => {
    setTemperature(0.7);
    setMaxTokens(4096);
    setSystemPrompt("You are OpenCoder, an AI coding assistant powered by Aider and OpenGPU.");
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50"
        onClick={() => setSettingsOpen(false)}
      />
      
      {/* Dialog */}
      <div className="relative bg-card border border-border rounded-lg shadow-xl w-full max-w-lg max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
          <div className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            <h2 className="text-lg font-semibold">Settings</h2>
          </div>
          <button
            onClick={() => setSettingsOpen(false)}
            className="p-1 hover:bg-muted rounded"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          {/* Model Selection */}
          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2">
              <MessageSquare className="w-4 h-4" />
              Model
            </label>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
            >
              {modelList.map((model) => (
                <option key={model.name} value={model.name}>
                  {model.name}
                </option>
              ))}
            </select>
          </div>

          {/* Temperature */}
          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2">
              <Thermometer className="w-4 h-4" />
              Temperature
              <span className="text-muted-foreground font-normal ml-auto">
                {temperature.toFixed(1)}
              </span>
            </label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={temperature}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Precise (0.0)</span>
              <span>Balanced (0.7)</span>
              <span>Creative (2.0)</span>
            </div>
          </div>

          {/* Max Tokens */}
          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Max Tokens
              <span className="text-muted-foreground font-normal ml-auto">
                {maxTokens}
              </span>
            </label>
            <input
              type="range"
              min="512"
              max="16384"
              step="512"
              value={maxTokens}
              onChange={(e) => setMaxTokens(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>512</span>
              <span>4096</span>
              <span>16384</span>
            </div>
          </div>

          {/* System Prompt */}
          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2">
              <MessageSquare className="w-4 h-4" />
              System Prompt
            </label>
            <textarea
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              rows={4}
              className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring resize-none font-mono text-sm"
              placeholder="You are OpenCoder, an AI coding assistant..."
            />
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-border bg-muted/30">
          <button
            onClick={handleReset}
            className="flex items-center gap-2 px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            Reset
          </button>
          <button
            onClick={() => {
              handleSave();
              setSettingsOpen(false);
            }}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-md transition-colors",
              saved 
                ? "bg-green-600 text-white"
                : "bg-primary text-primary-foreground hover:bg-primary/90"
            )}
          >
            {saved ? (
              <>
                <Check className="w-4 h-4" />
                Saved!
              </>
            ) : (
              "Apply"
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
