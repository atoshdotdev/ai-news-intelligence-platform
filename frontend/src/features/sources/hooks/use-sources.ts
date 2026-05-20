import { useQuery } from "@tanstack/react-query";
import { sourcesApi } from "@/features/sources/api/sources.api";
import type {
  UseSourcesParams,
  SourcesResponse,
} from "@/features/sources/types";

export function useSources(params?: UseSourcesParams) {
  return useQuery<SourcesResponse>({
    queryKey: ["sources", params],
    queryFn: () => sourcesApi.list(params),
  });
}
