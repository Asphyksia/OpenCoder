// =============================================================================
// TYPES - OpenCoder Frontend
// =============================================================================
// These types match the backend API responses from opencoder/models/schemas.py

// -----------------------------------------------------------------------------
// Agent Types
// -----------------------------------------------------------------------------

export type AgentStatus =
  | "ready"
  | "processing"
  | "busy"
  | "error"
  | "no_session";

// Note: "busy" is used in the frontend but not in backend status
// The backend returns status strings, frontend adds "no_session"

// -----------------------------------------------------------------------------
// Message Types
// -----------------------------------------------------------------------------

export type MessageRole = "user" | "assistant" | "system";

// Extended Message with UI status field for tracking message state
export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
  events?: AgentEvent[];
  fileChanges?: FileChange[];
  error?: string;
  // UI-specific fields (not from backend)
  status?: "sending" | "processing" | "success" | "error";
  model?: string;
  diffs?: string;
  duration?: number; // in milliseconds
}

// -----------------------------------------------------------------------------
// Model Types
// -----------------------------------------------------------------------------

export interface Model {
  id: string;
  name: string;
  provider: string;
  category?: string; // Used in UI dropdown
  type?: string; // Backend field - e.g., "text-to-text"
  context_length?: number;
  pricing?: {
    prompt: number;
    completion: number;
  };
}

// -----------------------------------------------------------------------------
// Agent Event Types
// -----------------------------------------------------------------------------

// Backend uses event_type as string, frontend maps to EventType
export type EventType =
  | "thinking"
  | "planning"
  | "action"
  | "tool"
  | "command"
  | "edit"
  | "read"
  | "browser"
  | "error"
  | "done";

// Backend EventSchema - uses event_type (snake_case)
export interface AgentEvent {
  id?: string;
  event_type: string; // Backend field name (snake_case)
  content: string;
  timestamp: string;
  details?: Record<string, unknown>;
}

// -----------------------------------------------------------------------------
// File Change Types
// -----------------------------------------------------------------------------

export type FileChangeType = "created" | "modified" | "deleted";

// Backend FileChangeSchema - uses operation (snake_case)
export interface FileChange {
  path?: string; // Frontend uses path
  filename?: string; // Backend field name
  type?: FileChangeType; // Frontend mapped type
  operation?: string; // Backend field name (created, modified, deleted)
  diff?: string;
}

// -----------------------------------------------------------------------------
// API Request/Response Types (matching backend schemas)
// -----------------------------------------------------------------------------

export interface ChatRequest {
  message: string;
  model: string;
  read_only?: boolean;
}

// Backend ChatResponse
export interface ChatResponse {
  success: boolean;
  message: string;
  events: AgentEvent[];
  file_changes: FileChange[];
  diffs: string;
  error?: string;
}

// Backend StatusResponse
export interface StatusResponse {
  status: string;
  repo_path: string;
  read_only: boolean;
  events_count: number;
  file_changes_count: number;
  available_models: string[];
  error?: string;
  session_id?: string | null;
}

// Backend doesn't have a /models endpoint with full details
// Frontend uses hardcoded models or gets model names from status
export interface ModelsResponse {
  models: Model[];
}

export interface HealthResponse {
  status: "ok" | "healthy" | "degraded" | "unhealthy";
  version: string;
}

// -----------------------------------------------------------------------------
// UI State Types
// -----------------------------------------------------------------------------

export interface Theme {
  theme: "light" | "dark" | "system";
  setTheme: (theme: "light" | "dark" | "system") => void;
}
