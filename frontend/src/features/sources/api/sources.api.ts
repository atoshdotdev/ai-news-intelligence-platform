import { request } from "@/lib/request";
import type {
  CreateSourceDTO,
  UseSourcesParams,
  SourcesResponse,
  Source,
} from "@/features/sources/types";

export const sourcesApi = {
  list: (params?: UseSourcesParams): Promise<SourcesResponse> =>
    request({
      url: "/sources",
      method: "GET",
      params,
    }),

  get: (id: string): Promise<Source> =>
    request({
      url: `/sources/${id}`,
      method: "GET",
    }),

  create: (data: CreateSourceDTO) =>
    request({
      url: "/sources",
      method: "POST",
      data,
    }),

  update: (id: string, data: CreateSourceDTO) =>
    request({
      url: `/sources/${id}`,
      method: "PUT",
      data,
    }),

  remove: (id: string) =>
    request({
      url: `/sources/${id}`,
      method: "DELETE",
    }),
};
