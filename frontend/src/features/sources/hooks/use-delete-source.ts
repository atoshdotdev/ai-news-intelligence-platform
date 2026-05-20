import { useMutation, useQueryClient } from "@tanstack/react-query";
import { sourcesApi } from "../api/sources.api";

export function useDeleteSource() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: sourcesApi.remove,

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sources"] });
    },
  });
}
