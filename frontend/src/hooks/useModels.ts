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
      
      // Filter to only show OpenGPU models (openai/ prefix or Qwen models)
      const openGpuModels = response.models.filter(
        (m) => m.name.startsWith("openai/") || m.name.includes("Qwen")
      );
      
      // Update available models with filtered list
      if (openGpuModels.length > 0) {
        setAvailableModels(openGpuModels);
        
        // Set to Qwen/Qwen3-Coder as default
        const qwenModel = openGpuModels.find(
          (m) => m.name.includes("Qwen3-Coder") || m.name.toLowerCase().includes("qwen")
        );
        setSelectedModel(qwenModel?.name || openGpuModels[0].name);
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
