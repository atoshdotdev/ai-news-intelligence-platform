import { useMutation, useQueryClient } from "@tanstack/react-query";
import { sourcesApi } from "../api/sources.api";
import { toast } from "sonner";

export function useDeleteSource() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: sourcesApi.remove,

    onSuccess: () => {
      toast.success("Source deleted successfully", { position: "top-center" });
      queryClient.invalidateQueries({ queryKey: ["sources"] });
    },
  });
}
