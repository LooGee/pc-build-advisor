import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";

export function useCompatibilityCheck(componentIds: Record<string, string>) {
  return useQuery({
    queryKey: ["compatibility", componentIds],
    queryFn: async () => {
      const response = await apiClient.post("/api/v1/compatibility/check", {
        component_ids: componentIds,
      });
      return response.data;
    },
    enabled: Object.keys(componentIds).length > 0,
  });
}
