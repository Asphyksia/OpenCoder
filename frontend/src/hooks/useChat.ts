import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAppStore } from "@/store/useAppStore";

export function useChat() {
  const queryClient = useQueryClient();
  const {
    addMessage,
    updateMessage,
    setAgentStatus,
    setIsProcessing,
    selectedModel,
    readOnly,
  } = useAppStore();

  const sendMessage = useMutation({
    mutationFn: async (message: string) => {
      // Validate model
      if (!selectedModel) {
        throw new Error("No model selected. Please wait for models to load.");
      }

      // Add user message
      const userMessage = addMessage({
        role: "user",
        content: message,
        status: "sending",
      });

      // Create placeholder for assistant response
      const assistantMessage = addMessage({
        role: "assistant",
        content: "",
        status: "processing",
        model: selectedModel,
      });

      setAgentStatus("busy");
      setIsProcessing(true);

      try {
        const response = await api.sendChat({
          message,
          model: selectedModel,
          read_only: readOnly,
        });

        return { userMessageId: userMessage.id, assistantMessageId: assistantMessage.id, response };
      } catch (error) {
        // Clean up messages on error
        updateMessage(userMessage.id, { status: "error" });
        updateMessage(assistantMessage.id, { 
          status: "error",
          error: error instanceof Error ? error.message : "Failed to send message"
        });
        setAgentStatus("error");
        setIsProcessing(false);
        throw error;
      }
    },
    onSuccess: ({ userMessageId, assistantMessageId, response }) => {
      // Update user message
      updateMessage(userMessageId, { status: "success" });

      // Update assistant message with response
      updateMessage(assistantMessageId, {
        content: response.message,
        status: response.success ? "success" : "error",
        events: response.events,
        fileChanges: response.file_changes,
        diffs: response.diffs,
        error: response.error || undefined,
      });

      if (response.success) {
        setAgentStatus("ready");
      } else {
        setAgentStatus("error");
      }

      setIsProcessing(false);
      queryClient.invalidateQueries({ queryKey: ["status"] });
    },
    onError: (error) => {
      console.error("Chat error:", error);
      setAgentStatus("error");
      setIsProcessing(false);
    },
  });

  return {
    sendMessage,
    isProcessing: useAppStore((state) => state.isProcessing),
  };
}
