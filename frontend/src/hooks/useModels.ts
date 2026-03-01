import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAppStore } from "@/store/useAppStore";

export function useModels() {
  const { setAvailableModels, setSelectedModel } = useAppStore();

  const modelsQuery = useQuery({
    queryKey: ["models"],
    queryFn: async () => {
      const response = await api.getModels();
      setAvailableModels(response.models);
      
      // Use all models from backend (already filtered to preferred models)
      const allModels = response.models;
      
      // Update available models with all models
      if (allModels.length > 0) {
        setAvailableModels(allModels);
        
        // Set to Qwen/Qwen3-Coder as default
        const defaultModel = allModels.find(
          (m) => m.name.includes("Qwen3-Coder") || m.name.toLowerCase().includes("qwen")
        );
        setSelectedModel(defaultModel?.name || allModels[0].name);
      } else if (response.models.length > 0) {
        setAvailableModels(response.models);
        setSelectedModel(response.models[0].name);
      }
      
      return response;
    },
    staleTime: 60000, // 1 minute
    retry: 2,
  });

  return {
    models: modelsQuery.data?.models ?? [],
    count: modelsQuery.data?.count ?? 0,
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
