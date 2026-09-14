import { useQuery } from "@tanstack/react-query";
import { eventsApi } from "@/features/events/api/events.api";
import type {
  EventDetail,
  EventsResponse,
  UseEventsParams,
} from "@/features/events/types";

export function useEvents(params?: UseEventsParams) {
  return useQuery<EventsResponse>({
    queryKey: ["events", params],
    queryFn: () => eventsApi.list(params),
  });
}

export function useEvent(id: string) {
  return useQuery<EventDetail>({
    queryKey: ["event", id],
    queryFn: () => eventsApi.get(id),
    enabled: !!id,
  });
}
