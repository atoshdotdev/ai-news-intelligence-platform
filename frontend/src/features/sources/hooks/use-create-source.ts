import { useMutation, useQueryClient } from "@tanstack/react-query";
import { sourcesApi } from "../api/sources.api";
import { toast } from "sonner";

export function useCreateSource() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: sourcesApi.create,

    onSuccess: () => {
      toast.success("Source created successfully", { position: "top-center" });
      queryClient.invalidateQueries({ queryKey: ["sources"] });
    },
  });
}
