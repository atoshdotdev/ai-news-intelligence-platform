import { request } from "@/lib/request";
import { BlacklistEntry, CreateBlacklistDTO } from "@/features/sources/types";

export const blacklistApi = {
  list: (sourceId: string): Promise<BlacklistEntry[]> =>
    request({
      url: `/sources/${sourceId}/blacklist`,
      method: "GET",
    }),

  create: (sourceId: string, data: CreateBlacklistDTO) =>
    request({
      url: `/sources/${sourceId}/blacklist`,
      method: "POST",
      data,
    }),

  remove: (sourceId: string, entryId: string) =>
    request({
      url: `/sources/${sourceId}/blacklist/${entryId}`,
      method: "DELETE",
    }),
};
