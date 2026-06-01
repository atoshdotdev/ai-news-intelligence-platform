import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { sourcesApi } from "@/features/sources/api/sources.api";
import type {
  UseSourcesParams,
  SourcesResponse,
} from "@/features/sources/types";
import { SourceFormValues } from "@/features/sources/schemas/source.schema";
import { toast } from "sonner";

export function useSources(params?: UseSourcesParams) {
  return useQuery<SourcesResponse>({
    queryKey: ["sources", params],
    queryFn: () => sourcesApi.list(params),
  });
}

export function useSource(id: string) {
  return useQuery({
    queryKey: ["source", id],
    queryFn: () => sourcesApi.get(id),
    enabled: !!id,
  });
}

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

export function useUpdateSource() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: SourceFormValues }) =>
      sourcesApi.update(id, data),

    onSuccess: () => {
      toast.success("Source updated successfully", { position: "top-center" });
      queryClient.invalidateQueries({ queryKey: ["sources"] });
    },
  });
}

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
