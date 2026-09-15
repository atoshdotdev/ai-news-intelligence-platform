"use client";

import Image from "next/image";
import Link from "next/link";
import { ArrowLeft, CalendarDays, ExternalLink, Newspaper } from "lucide-react";

import { useEvent } from "@/features/events/hooks/use-events";
import { Spinner } from "@/components/ui/spinner";

type EventDetailPageProps = {
  id: string;
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

function formatShortDate(date: string | null) {
  if (!date) {
    return null;
  }

  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
  }).format(new Date(date));
}

function formatEntityLabel(label: string) {
  return label
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

export function EventDetailPage({ id }: EventDetailPageProps) {
  const { data: event, isLoading, isError } = useEvent(id);

  if (isLoading) {
    return (
      <div className="flex h-full justify-center items-center py-10">
        <Spinner className="size-6" />
      </div>
    );
  }

  if (isError || !event) {
    return (
      <main className="mx-auto max-w-5xl px-4 py-8">
        <Link
          href="/feed"
          className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="size-4" />
          Back to feed
        </Link>

        <div className="py-16 text-center">
          <h1 className="text-xl font-semibold">Event not found</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            The event could not be loaded.
          </p>
        </div>
      </main>
    );
  }

  const sourceCounts = event.articles.reduce<Record<string, number>>(
    (counts, article) => {
      counts[article.source_name] = (counts[article.source_name] ?? 0) + 1;

      return counts;
    },
    {},
  );

  const sourceEntries = Object.entries(sourceCounts).sort(
    ([, countA], [, countB]) => countB - countA,
  );

  const sortedArticles = [...event.articles].sort((articleA, articleB) => {
    if (!articleA.published_at) {
      return 1;
    }

    if (!articleB.published_at) {
      return -1;
    }

    return (
      new Date(articleB.published_at).getTime() -
      new Date(articleA.published_at).getTime()
    );
  });

  const uniqueSources = new Set(
    event.articles.map((article) => article.source_name),
  ).size;

  const groupedEntities = event.entities?.reduce<Record<string, string[]>>(
    (groups, entity) => {
      const value = entity.value.trim();

      if (!value) {
        return groups;
      }

      if (!groups[entity.label]) {
        groups[entity.label] = [];
      }

      if (!groups[entity.label].includes(value)) {
        groups[entity.label].push(value);
      }

      return groups;
    },
    {},
  );

  return (
    <main className="mx-auto max-w-5xl px-4 py-8">
      <Link
        href="/feed"
        className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
      >
        <ArrowLeft className="size-4" />
        Back to feed
      </Link>

      <div className="mt-8">
        {event.category && (
          <span className="rounded-md bg-muted px-2 py-1 text-xs font-medium capitalize">
            {event.category}
          </span>
        )}

        <h1 className="mt-4 max-w-4xl text-3xl font-bold tracking-tight leading-normal md:text-4xl">
          {event.title ?? "Untitled event"}
        </h1>

        <div className="mt-4 flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
          {event.last_published_at && (
            <span className="flex items-center gap-1.5">
              <CalendarDays className="size-4" />
              Updated {formatDate(event.last_published_at)}
            </span>
          )}

          <span className="flex items-center gap-1.5">
            <Newspaper className="size-4" />
            {event.articles.length}{" "}
            {event.articles.length === 1 ? "article" : "articles"}
          </span>
        </div>
      </div>

      {event.image_url && (
        <div className="relative mt-8 aspect-video overflow-hidden rounded-xl bg-muted">
          <Image
            src={event.image_url}
            alt={event.title ?? "Event image"}
            fill
            className="object-cover"
            sizes="(min-width: 1024px) 1024px, 100vw"
          />
        </div>
      )}

      {event.summary && (
        <section className="mt-10">
          <h2 className="text-xl font-semibold tracking-tight">Summary</h2>

          <p className="mt-4 max-w-4xl text-base leading-7 text-muted-foreground">
            {event.summary}
          </p>
        </section>
      )}

      <section className="mt-10">
        <h2 className="text-xl font-semibold tracking-tight">Coverage</h2>

        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <div className="rounded-xl border bg-card p-5">
            <p className="text-sm text-muted-foreground">Articles</p>
            <p className="mt-1 text-2xl font-semibold">
              {event.articles.length}
            </p>
          </div>

          <div className="rounded-xl border bg-card p-5">
            <p className="text-sm text-muted-foreground">Sources</p>
            <p className="mt-1 text-2xl font-semibold">{uniqueSources}</p>
          </div>
        </div>

        {sourceEntries.length > 0 && (
          <div className="mt-6 rounded-xl border bg-card p-5">
            <h3 className="font-medium">Coverage by source</h3>

            <div className="mt-5 space-y-4">
              {sourceEntries.map(([source, count]) => {
                const percentage =
                  event.articles.length > 0
                    ? (count / event.articles.length) * 100
                    : 0;

                return (
                  <div key={source}>
                    <div className="mb-1.5 flex items-center justify-between text-sm">
                      <span className="font-medium">{source}</span>
                      <span className="text-muted-foreground">
                        {count} {count === 1 ? "article" : "articles"}
                      </span>
                    </div>

                    <div className="h-2 overflow-hidden rounded-full bg-muted">
                      <div
                        className="h-full rounded-full bg-foreground transition-all"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </section>

      {event.entities && event.entities.length > 0 && (
        <section className="mt-10">
          <h2 className="text-xl font-semibold tracking-tight">Key entities</h2>

          <div className="mt-4 space-y-5">
            {Object.entries(groupedEntities ?? {}).map(([label, entities]) => (
              <div key={label}>
                <h3 className="text-sm font-medium capitalize text-muted-foreground">
                  {formatEntityLabel(label)}
                </h3>

                <div className="mt-2 flex flex-wrap gap-2">
                  {entities.map((value) => (
                    <span
                      key={`${label}-${value}`}
                      className="rounded-md border bg-muted/50 px-3 py-1.5 text-sm"
                    >
                      {value}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="mt-10">
        <h2 className="text-xl font-semibold tracking-tight">Timeline</h2>

        <div className="mt-6 space-y-6">
          {sortedArticles.map((article, index) => (
            <div key={article.id} className="relative flex gap-4">
              <div className="flex flex-col items-center">
                <div className="mt-1.5 size-3 shrink-0 rounded-full bg-foreground" />

                {index < sortedArticles.length - 1 && (
                  <div className="mt-2 h-full w-px bg-border" />
                )}
              </div>

              <div className="pb-2">
                <p className="text-xs text-muted-foreground">
                  {formatShortDate(article.published_at)}
                </p>

                <p className="mt-1 font-medium">{article.source_name}</p>

                <p className="mt-1 text-sm text-muted-foreground">
                  {article.title}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="mt-10 pb-12">
        <h2 className="text-xl font-semibold tracking-tight">
          Related coverage
        </h2>

        <div className="mt-6 space-y-4">
          {event.articles.map((article) => (
            <article
              key={article.id}
              className="overflow-hidden rounded-xl border bg-card transition-colors hover:bg-accent/50"
            >
              <div className="flex flex-col sm:flex-row">
                {article.image_url && (
                  <div className="relative aspect-video w-full shrink-0 overflow-hidden bg-muted sm:aspect-auto sm:h-auto sm:w-48">
                    <Image
                      src={article.image_url}
                      alt=""
                      fill
                      className="object-cover"
                      sizes="192px"
                    />
                  </div>
                )}

                <div className="flex flex-1 flex-col p-5">
                  <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                    <span className="font-medium text-foreground">
                      {article.source_name}
                    </span>

                    {article.published_at && (
                      <>
                        <span>·</span>
                        <span>{formatDate(article.published_at)}</span>
                      </>
                    )}
                  </div>

                  <h3 className="mt-2 text-base font-semibold tracking-tight">
                    {article.title}
                  </h3>

                  <div className="mt-auto pt-4">
                    <a
                      href={article.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 text-sm font-medium hover:underline"
                    >
                      Read article
                      <ExternalLink className="size-3.5" />
                    </a>
                  </div>
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
