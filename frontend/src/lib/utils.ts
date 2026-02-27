// =============================================================================
// UTILITIES - OpenCoder Frontend
// =============================================================================

import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

// -----------------------------------------------------------------------------
// Class Name Utilities
// -----------------------------------------------------------------------------

/**
 * Combines class names with tailwind-merge for proper conflict resolution
 * @param inputs - Class values to combine
 * @returns Merged class string
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

// -----------------------------------------------------------------------------
// ID Generation
// -----------------------------------------------------------------------------

/**
 * Generates a unique ID
 * @returns Unique string ID
 */
export function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
}

// -----------------------------------------------------------------------------
// Date/Time Formatting
// -----------------------------------------------------------------------------

/**
 * Formats a timestamp to a readable time string
 * @param timestamp - ISO timestamp string
 * @returns Formatted time string (HH:MM:SS)
 */
export function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

/**
 * Formats duration in milliseconds to a readable string
 * @param ms - Duration in milliseconds
 * @returns Formatted duration string
 */
export function formatDuration(ms: number): string {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);

  if (hours > 0) {
    return `${hours}h ${minutes % 60}m ${seconds % 60}s`;
  }
  if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`;
  }
  return `${seconds}s`;
}

/**
 * Formats a relative time (e.g., "2 minutes ago")
 * @param timestamp - ISO timestamp string
 * @returns Relative time string
 */
export function formatRelativeTime(timestamp: string): string {
  const now = new Date();
  const date = new Date(timestamp);
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  if (diffDay > 0) {
    return `${diffDay}d ago`;
  }
  if (diffHour > 0) {
    return `${diffHour}h ago`;
  }
  if (diffMin > 0) {
    return `${diffMin}m ago`;
  }
  return "just now";
}

// -----------------------------------------------------------------------------
// String Utilities
// -----------------------------------------------------------------------------

/**
 * Truncates a string to a maximum length
 * @param str - String to truncate
 * @param maxLength - Maximum length
 * @returns Truncated string with ellipsis if needed
 */
export function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength - 3) + "...";
}

/**
 * Extracts file name from a path
 * @param filePath - File path
 * @returns File name
 */
export function getFileName(filePath: string): string {
  return filePath.split("/").pop() || filePath;
}

// -----------------------------------------------------------------------------
// File Change Utilities
// -----------------------------------------------------------------------------

/**
 * Maps backend operation to FileChangeType
 * @param operation - Backend operation string
 * @returns FileChangeType
 */
export function mapOperationToType(
  operation?: string
): "created" | "modified" | "deleted" {
  switch (operation) {
    case "created":
      return "created";
    case "deleted":
      return "deleted";
    default:
      return "modified";
  }
}

// -----------------------------------------------------------------------------
// Event Type Utilities
// -----------------------------------------------------------------------------

/**
 * Checks if an event type represents a thinking state
 * @param eventType - Event type string
 * @returns True if thinking state
 */
export function isThinkingEvent(eventType: string): boolean {
  return eventType === "thinking" || eventType === "planning";
}

// -----------------------------------------------------------------------------
// Debounce Utility
// -----------------------------------------------------------------------------

/**
 * Creates a debounced function
 * @param fn - Function to debounce
 * @param delay - Delay in milliseconds
 * @returns Debounced function
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
}
