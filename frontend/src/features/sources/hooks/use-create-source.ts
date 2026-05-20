import { useMutation, useQueryClient } from "@tanstack/react-query";
import { sourcesApi } from "../api/sources.api";

export function useCreateSource() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: sourcesApi.create,

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sources"] });
    },
  });
}
