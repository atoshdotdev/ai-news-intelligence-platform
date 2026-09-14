import Image from "next/image";
import { CalendarDays, Newspaper } from "lucide-react";

type Event = {
  id: string;
  title: string | null;
  summary: string | null;
  category: string | null;
  image_url: string | null;
  last_published_at: string | null;
  article_count: number;
};

type EventCardProps = {
  event: Event;
};

function formatDate(date: string | null) {
  if (!date) {
    return null;
  }

  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(date));
}

export function EventCard({ event }: EventCardProps) {
  return (
    <article className="group flex h-full flex-col overflow-hidden rounded-xl border bg-card transition-colors hover:bg-accent/50">
      <div className="relative aspect-video w-full overflow-hidden bg-muted">
        {event.image_url ? (
          <Image
            src={event.image_url}
            alt={event.title ?? "Event image"}
            fill
            className="object-cover transition-transform duration-300 group-hover:scale-105"
            sizes="(min-width: 1024px) 33vw, (min-width: 768px) 50vw, 100vw"
          />
        ) : (
          <div className="flex size-full items-center justify-center text-muted-foreground">
            <Newspaper className="size-10 opacity-30" />
          </div>
        )}
      </div>

      <div className="flex h-full flex-col p-5">
        <div className="mb-3 flex items-center justify-between gap-3">
          {event.category && (
            <span className="rounded-md bg-muted px-2 py-1 text-xs font-medium capitalize">
              {event.category}
            </span>
          )}
        </div>

        <h2 className="line-clamp-2 text-lg font-semibold tracking-tight">
          {event.title ?? "Untitled event"}
        </h2>

        {event.summary && (
          <p className="mt-3 line-clamp-4 text-sm leading-6 text-muted-foreground">
            {event.summary}
          </p>
        )}

        <div className="mt-auto flex flex-wrap items-center gap-4 pt-5 text-xs text-muted-foreground">
          <span className="flex items-center gap-1.5">
            <Newspaper className="size-3.5" />
            {event.article_count}{" "}
            {event.article_count === 1 ? "article" : "articles"}
          </span>

          {event.last_published_at && (
            <span className="flex items-center gap-1.5">
              <CalendarDays className="size-3.5" />
              {formatDate(event.last_published_at)}
            </span>
          )}
        </div>
      </div>
    </article>
  );
}
