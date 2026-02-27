// =============================================================================
// API CLIENT - OpenCoder Frontend
// =============================================================================

import type {
  ChatRequest,
  ChatResponse,
  StatusResponse,
  HealthResponse,
  Model,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// -----------------------------------------------------------------------------
// API Client
// -----------------------------------------------------------------------------

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `HTTP error ${response.status}`);
    }

    return response.json();
  }

  // -------------------------------------------------------------------------
  // Chat
  // -------------------------------------------------------------------------

  /**
   * Send a chat message to the agent
   */
  async sendChat(request: ChatRequest): Promise<ChatResponse> {
    return this.request<ChatResponse>("/chat", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  // -------------------------------------------------------------------------
  // Status
  // -------------------------------------------------------------------------

  /**
   * Get current agent status
   */
  async getStatus(): Promise<StatusResponse> {
    return this.request<StatusResponse>("/status");
  }

  // -------------------------------------------------------------------------
  // Models
  // -------------------------------------------------------------------------

  /**
   * Get available models from the API
   */
  async getModels(): Promise<{ models: Model[]; count: number }> {
    return this.request<{ models: Model[]; count: number }>("/models");
  }

  // -------------------------------------------------------------------------
  // Health
  // -------------------------------------------------------------------------

  /**
   * Check API health status
   */
  async health(): Promise<HealthResponse> {
    return this.request<HealthResponse>("/health");
  }
}

// -----------------------------------------------------------------------------
// Export singleton instance
// -----------------------------------------------------------------------------

export const api = new ApiClient(API_BASE_URL);

// -----------------------------------------------------------------------------
// Export individual functions for convenience
// -----------------------------------------------------------------------------

export const sendChat = (request: ChatRequest) => api.sendChat(request);
export const getStatus = () => api.getStatus();
export const getModels = () => api.getModels();
export const health = () => api.health();
