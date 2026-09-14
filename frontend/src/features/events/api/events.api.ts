import { request } from "@/lib/request";
import type {
  EventDetail,
  EventsResponse,
  UseEventsParams,
} from "@/features/events/types";

export const eventsApi = {
  list: (params?: UseEventsParams): Promise<EventsResponse> =>
    request({
      url: "/events",
      method: "GET",
      params,
    }),

  get: (id: string): Promise<EventDetail> =>
    request({
      url: `/events/${id}`,
      method: "GET",
    }),
};
