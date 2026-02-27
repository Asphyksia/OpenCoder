"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { ChevronDown, ChevronUp, Copy, Check } from "lucide-react";

interface DiffViewerProps {
  diffs: string;
  maxLines?: number;
}

export function DiffViewer({ diffs, maxLines = 20 }: DiffViewerProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const diffLines = diffs.split("\n");
  const shouldTruncate = diffLines.length > maxLines;
  const displayLines = isExpanded || !shouldTruncate ? diffLines : diffLines.slice(0, maxLines);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(diffs);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="border border-border rounded-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 bg-muted border-b border-border">
        <span className="text-xs font-medium">Diff</span>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleCopy}
            className="h-7 px-2"
          >
            {copied ? (
              <Check className="w-3 h-3 text-green-500" />
            ) : (
              <Copy className="w-3 h-3" />
            )}
          </Button>
          {shouldTruncate && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
              className="h-7 px-2"
            >
              {isExpanded ? (
                <ChevronUp className="w-3 h-3" />
              ) : (
                <ChevronDown className="w-3 h-3" />
              )}
              <span className="ml-1 text-xs">
                {isExpanded ? "Less" : `+${diffLines.length - maxLines} more`}
              </span>
            </Button>
          )}
        </div>
      </div>

      {/* Diff content */}
      <div className="overflow-x-auto">
        <pre className="text-xs font-mono p-3 bg-muted/30">
          {displayLines.map((line, idx) => {
            const isAdded = line.startsWith("+") && !line.startsWith("+++");
            const isRemoved = line.startsWith("-") && !line.startsWith("---");
            const isHeader = line.startsWith("@@");

            return (
              <div
                key={idx}
                className={cn(
                  "px-2 py-0.5",
                  isAdded && "bg-green-500/20 text-green-400",
                  isRemoved && "bg-red-500/20 text-red-400",
                  isHeader && "text-blue-400 bg-blue-500/10"
                )}
              >
                {line}
              </div>
            );
          })}
        </pre>
      </div>
    </div>
  );
}
