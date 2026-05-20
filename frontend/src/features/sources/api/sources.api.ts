import { request } from "@/lib/request";
import type {
  CreateSourceDTO,
  UseSourcesParams,
  SourcesResponse,
} from "@/features/sources/types";

export const sourcesApi = {
  list: (params?: UseSourcesParams): Promise<SourcesResponse> =>
    request({
      url: "/sources",
      method: "GET",
      params,
    }),

  get: (id: number) =>
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

  update: (id: number, data: CreateSourceDTO) =>
    request({
      url: `/sources/${id}`,
      method: "PUT",
      data,
    }),

  remove: (id: number) =>
    request({
      url: `/sources/${id}`,
      method: "DELETE",
    }),
};
