import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { blacklistApi } from "@/features/sources/api/blacklist.api";
import { toast } from "sonner";

export function useBlacklist(sourceId?: string) {
  return useQuery({
    queryKey: ["blacklist", sourceId],
    queryFn: () => blacklistApi.list(sourceId!),
    enabled: !!sourceId,
  });
}

export function useCreateBlacklist(sourceId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { url_fragment: string }) =>
      blacklistApi.create(sourceId, data),

    onSuccess: () => {
      toast.success("Added to blacklist", { position: "top-center" });
      queryClient.invalidateQueries({ queryKey: ["blacklist", sourceId] });
    },
  });
}

export function useDeleteBlacklist(sourceId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (entryId: string) => blacklistApi.remove(sourceId, entryId),

    onSuccess: () => {
      toast.success("Removed from blacklist", { position: "top-center" });
      queryClient.invalidateQueries({ queryKey: ["blacklist", sourceId] });
    },
  });
}
