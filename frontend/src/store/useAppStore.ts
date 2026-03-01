import { create } from "zustand";
import { persist } from "zustand/middleware";
import { AgentStatus, Message, Model } from "@/lib/types";
import { generateId } from "@/lib/utils";

// Conversation interface
export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  model: string;
  createdAt: string;
  updatedAt: string;
  pinned: boolean;
}

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
  
  // Conversation Panel
  panelOpen: boolean;
  setPanelOpen: (open: boolean) => void;
  
  // Conversations
  conversations: Conversation[];
  activeConversationId: string | null;
  createConversation: () => string;
  loadConversation: (id: string) => void;
  deleteConversation: (id: string) => void;
  saveCurrentConversation: () => void;
  updateConversationTitle: (id: string, title: string) => void;
  pinConversation: (id: string) => void;
  
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
      
      // Conversation Panel
      panelOpen: false,
      setPanelOpen: (open) => {
        set({ panelOpen: open });
      },
      
      // Conversations
      conversations: [],
      activeConversationId: null,
      
      createConversation: () => {
        const id = generateId();
        const newConv: Conversation = {
          id,
          title: 'Nueva conversación',
          messages: [],
          model: get().selectedModel || 'Qwen/Qwen3-Coder',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          pinned: false,
        };
        set(state => ({
          conversations: [newConv, ...state.conversations],
          activeConversationId: id,
          messages: [],
        }));
        return id;
      },
      
      loadConversation: (id) => {
        const conv = get().conversations.find(c => c.id === id);
        if (conv) {
          set({
            activeConversationId: id,
            messages: conv.messages,
            selectedModel: conv.model,
          });
        }
      },
      
      deleteConversation: (id) => {
        set(state => ({
          conversations: state.conversations.filter(c => c.id !== id),
          activeConversationId: state.activeConversationId === id ? null : state.activeConversationId,
          messages: state.activeConversationId === id ? [] : state.messages,
        }));
      },
      
      saveCurrentConversation: () => {
        const { activeConversationId, conversations, messages, selectedModel } = get();
        if (!activeConversationId || messages.length === 0) return;
        
        // Generate title from first user message
        const firstUserMsg = messages.find(m => m.role === 'user');
        const title = firstUserMsg?.content.slice(0, 40) || 'Conversación';
        
        set(state => ({
          conversations: state.conversations.map(c => 
            c.id === activeConversationId 
              ? { ...c, messages, model: selectedModel, title, updatedAt: new Date().toISOString() }
              : c
          )
        }));
      },
      
      updateConversationTitle: (id, title) => {
        set(state => ({
          conversations: state.conversations.map(c =>
            c.id === id ? { ...c, title, updatedAt: new Date().toISOString() } : c
          )
        }));
      },
      
      pinConversation: (id) => {
        set(state => ({
          conversations: state.conversations.map(c =>
            c.id === id ? { ...c, pinned: !c.pinned } : c
          )
        }));
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
        conversations: state.conversations,
        activeConversationId: state.activeConversationId,
        panelOpen: state.panelOpen,
      }),
    }
  )
);
