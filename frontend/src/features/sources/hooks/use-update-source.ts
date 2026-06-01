import { useMutation, useQueryClient } from "@tanstack/react-query";
import { sourcesApi } from "@/features/sources/api/sources.api";
import { SourceFormValues } from "@/features/sources/schemas/source.schema";
import { toast } from "sonner";

export function useUpdateSource() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: SourceFormValues }) =>
      sourcesApi.update(id, data),

    onSuccess: () => {
      toast.success("Source updated successfully", { position: "top-center" });
      queryClient.invalidateQueries({ queryKey: ["sources"] });
    },
  });
}
