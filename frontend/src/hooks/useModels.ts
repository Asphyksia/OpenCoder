import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAppStore } from "@/store/useAppStore";

export function useModels() {
  const { setAvailableModels, setSelectedModel } = useAppStore();

  const modelsQuery = useQuery({
    queryKey: ["models"],
    queryFn: async () => {
      const models = await api.getModels();
      setAvailableModels(models);
      
      // Always set to first available model when models are loaded
      if (models.length > 0) {
        setSelectedModel(models[0].name);
      }
      
      return models;
    },
    staleTime: 60000, // 1 minute
    retry: 2,
  });

  return {
    models: modelsQuery.data ?? [],
    count: modelsQuery.data?.length ?? 0,
    isLoading: modelsQuery.isLoading,
    error: modelsQuery.error,
    refetch: modelsQuery.refetch,
  };
}

// Note: getPricing is not implemented in the backend API yet
export function usePricing() {
  const pricingQuery = useQuery({
    queryKey: ["pricing"],
    queryFn: async () => {
      // Placeholder - backend doesn't have pricing endpoint
      return { models: [] };
    },
    staleTime: 300000, // 5 minutes
    retry: 1,
    enabled: false, // Disabled until backend supports it
  });

  return pricingQuery;
}
