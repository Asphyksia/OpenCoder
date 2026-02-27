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
      
      // Always set to first available model when models are loaded
      if (response.models.length > 0) {
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

export function usePricing() {
  const pricingQuery = useQuery({
    queryKey: ["pricing"],
    queryFn: api.getPricing,
    staleTime: 300000, // 5 minutes
    retry: 1,
  });

  return pricingQuery;
}
