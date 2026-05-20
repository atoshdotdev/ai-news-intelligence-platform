import { useMutation, useQueryClient } from "@tanstack/react-query";
import { sourcesApi } from "@/features/sources/api/sources.api";
import { SourceFormValues } from "@/features/sources/schemas/source.schema";

export function useUpdateSource() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: SourceFormValues }) =>
      sourcesApi.update(id, data),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sources"] });
    },
  });
}
