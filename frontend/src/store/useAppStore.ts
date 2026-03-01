import { create } from "zustand";
import { persist } from "zustand/middleware";
import { AgentStatus, Message, Model } from "@/lib/types";
import { generateId } from "@/lib/utils";

interface AppStore {
  // Messages
  messages: Message[];
  addMessage: (message: Omit<Message, "id" | "timestamp">) => Message;
  updateMessage: (id: string, updates: Partial<Message>) => void;
  clearMessages: () => void;

  // Agent Status
  agentStatus: AgentStatus;
  setAgentStatus: (status: AgentStatus) => void;

  // Model
  selectedModel: string;
  setSelectedModel: (model: string) => void;
  availableModels: Model[];
  setAvailableModels: (models: Model[]) => void;

  // Session
  readOnly: boolean;
  setReadOnly: (readOnly: boolean) => void;
  repoPath: string;
  setRepoPath: (path: string) => void;
  sessionId: string | null;
  setSessionId: (id: string | null) => void;

  // UI State
  isProcessing: boolean;
  setIsProcessing: (processing: boolean) => void;
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  
  // Settings
  settingsOpen: boolean;
  setSettingsOpen: (open: boolean) => void;
  
  // Model Settings
  temperature: number;
  setTemperature: (temp: number) => void;
  maxTokens: number;
  setMaxTokens: (tokens: number) => void;
  systemPrompt: string;
  setSystemPrompt: (prompt: string) => void;
}

export const useAppStore = create<AppStore>()(
  persist(
    (set, get) => ({
      // Messages
      messages: [],

      addMessage: (message) => {
        const newMessage: Message = {
          ...message,
          id: generateId(),
          timestamp: new Date().toISOString(),
        };
        set((state) => ({
          messages: [...state.messages, newMessage],
        }));
        return newMessage;
      },

      updateMessage: (id, updates) => {
        set((state) => ({
          messages: state.messages.map((msg) =>
            msg.id === id ? { ...msg, ...updates } : msg
          ),
        }));
      },

      clearMessages: () => {
        set({ messages: [] });
      },

      // Agent Status
      agentStatus: "ready",
      setAgentStatus: (status) => {
        set({ agentStatus: status });
      },

      // Model
      selectedModel: "",
      setSelectedModel: (model) => {
        set({ selectedModel: model });
      },
      availableModels: [],
      setAvailableModels: (models) => {
        set({ availableModels: models });
      },

      // Session
      readOnly: false,
      setReadOnly: (readOnly) => {
        set({ readOnly });
      },
      repoPath: "./workspace",
      setRepoPath: (path) => {
        set({ repoPath: path });
      },
      sessionId: null,
      setSessionId: (id) => {
        set({ sessionId: id });
      },

      // UI State
      isProcessing: false,
      setIsProcessing: (processing) => {
        set({ isProcessing: processing });
      },
      sidebarOpen: true,
      setSidebarOpen: (open) => {
        set({ sidebarOpen: open });
      },
      
      // Settings
      settingsOpen: false,
      setSettingsOpen: (open) => {
        set({ settingsOpen: open });
      },
      
      // Model Settings
      temperature: 0.7,
      setTemperature: (temp) => {
        set({ temperature: temp });
      },
      maxTokens: 4096,
      setMaxTokens: (tokens) => {
        set({ maxTokens: tokens });
      },
      systemPrompt: "You are OpenCoder, an AI coding assistant powered by Aider and OpenGPU.",
      setSystemPrompt: (prompt) => {
        set({ systemPrompt: prompt });
      },
    }),
    {
      name: "opencoder-storage",
      partialize: (state) => ({
        readOnly: state.readOnly,
        repoPath: state.repoPath,
        messages: state.messages,
        temperature: state.temperature,
        maxTokens: state.maxTokens,
        systemPrompt: state.systemPrompt,
      }),
    }
  )
);
