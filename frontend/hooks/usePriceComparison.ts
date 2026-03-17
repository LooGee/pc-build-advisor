import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";

export function usePriceComparison(componentId: string) {
  return useQuery({
    queryKey: ["prices", componentId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/v1/components/${componentId}/prices`);
      return response.data;
    },
    enabled: !!componentId,
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
}
