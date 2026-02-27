import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAppStore } from "@/store/useAppStore";
import type { AgentStatus } from "@/lib/types";

const STATUS_REFRESH_INTERVAL = 5000; // 5 seconds

export function useStatus() {
  const queryClient = useQueryClient();
  const { setAgentStatus, setRepoPath } = useAppStore();

  const statusQuery = useQuery({
    queryKey: ["status"],
    queryFn: async () => {
      try {
        const status = await api.getStatus();
        // Map status string to AgentStatus type
        const mappedStatus = status.status as AgentStatus;
        // Keep status as ready if backend returns no_session
        // (agent is ready to receive messages and create a session)
        if (status.status !== "no_session") {
          setAgentStatus(mappedStatus);
        } else {
          setAgentStatus("ready");
        }
        setRepoPath(status.repo_path);
        return status;
      } catch (error) {
        // If we can't get status, don't change the status
        console.error("Failed to get status:", error);
        throw error;
      }
    },
    refetchInterval: STATUS_REFRESH_INTERVAL,
    retry: 1,
    staleTime: 3000,
    enabled: true, // Always run
  });

  const refetchStatus = () => {
    queryClient.invalidateQueries({ queryKey: ["status"] });
  };

  return {
    status: statusQuery.data,
    isLoading: statusQuery.isLoading,
    error: statusQuery.error,
    refetchStatus,
  };
}

export function useHealthCheck() {
  const healthQuery = useQuery({
    queryKey: ["health"],
    queryFn: api.health,
    refetchInterval: 30000,
    retry: 1,
  });

  return {
    isHealthy: healthQuery.data?.status === "ok" || healthQuery.data?.status === "healthy",
    ...healthQuery,
  };
}
