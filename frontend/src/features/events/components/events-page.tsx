"use client";

import { useEvents } from "@/features/events/hooks/use-events";
import { EventCard } from "@/features/events/components/event-card";

export function EventsPage() {
  const { data, isLoading, isError } = useEvents({
    page: 1,
    size: 12,
  });

  if (isLoading) {
    return <div>Loading events...</div>;
  }

  if (isError) {
    return <div>Failed to load events.</div>;
  }

  return (
    <main className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold tracking-tight">News</h1>
        <p className="mt-2 text-muted-foreground">
          Explore the latest news events and coverage from multiple sources.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {data?.items.map((event) => (
          <EventCard key={event.id} event={event} />
        ))}
      </div>
    </main>
  );
}
