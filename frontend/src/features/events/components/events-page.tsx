"use client";

import { useEffect, useState } from "react";
import { CalendarIcon, Search, SlidersHorizontal, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Input } from "@/components/ui/input";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Spinner } from "@/components/ui/spinner";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import { EventCard } from "@/features/events/components/event-card";
import { useEvents } from "@/features/events/hooks/use-events";
import { useCategories } from "@/features/categories/hooks/use-categories";

function formatDate(date: Date | undefined) {
  if (!date) {
    return "";
  }

  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
  }).format(date);
}

function formatDateParam(date: Date | undefined) {
  if (!date) {
    return undefined;
  }

  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
}

function parseDate(value: string) {
  if (!value) {
    return undefined;
  }

  const [year, month, day] = value.split("-").map(Number);

  return new Date(year, month - 1, day);
}

function EventCardSkeleton() {
  return (
    <div className="overflow-hidden rounded-xl border bg-card">
      <div className="aspect-video animate-pulse bg-muted" />

      <div className="space-y-3 p-5">
        <div className="h-5 w-24 animate-pulse rounded bg-muted" />
        <div className="h-6 w-4/5 animate-pulse rounded bg-muted" />
        <div className="h-4 w-full animate-pulse rounded bg-muted" />
        <div className="h-4 w-3/4 animate-pulse rounded bg-muted" />
      </div>
    </div>
  );
}

export function EventsPage() {
  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("all");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [page, setPage] = useState(1);

  const { data: categoriesData, isLoading: isCategoriesLoading } =
    useCategories();

  const categories = categoriesData?.categories ?? [];

  useEffect(() => {
    const timeout = setTimeout(() => {
      setSearch(searchInput.trim());
      setPage(1);
    }, 400);

    return () => clearTimeout(timeout);
  }, [searchInput]);

  const { data, isLoading, isFetching, isError } = useEvents({
    page,
    size: 12,
    search: search || undefined,
    category: category === "all" ? undefined : category,
    from_date: fromDate || undefined,
    to_date: toDate || undefined,
  });

  const events = data?.items ?? [];
  const pagination = data?.pagination;

  const hasFilters =
    searchInput.trim() !== "" ||
    category !== "all" ||
    fromDate !== "" ||
    toDate !== "";

  const hasEvents = events.length > 0 || (pagination?.total_items ?? 0) > 0;

  function clearFilters() {
    setSearchInput("");
    setSearch("");
    setCategory("all");
    setFromDate("");
    setToDate("");
    setPage(1);
  }

  function handleCategoryChange(value: string | null) {
    setCategory(value ?? "all");
    setPage(1);
  }

  function handleFromDateChange(date: Date | undefined) {
    setFromDate(formatDateParam(date) ?? "");
    setPage(1);
  }

  function handleToDateChange(date: Date | undefined) {
    setToDate(formatDateParam(date) ?? "");
    setPage(1);
  }

  if (isError) {
    return (
      <main className="container mx-auto p-6">
        <div className="rounded-xl border p-8 text-center">
          <h2 className="font-semibold">Failed to load events</h2>

          <p className="mt-1 text-sm text-muted-foreground">
            Something went wrong while loading the news.
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className="container mx-auto p-6">
      {(hasEvents || hasFilters) && (
        <section className="mb-8 rounded-xl border bg-card p-4">
          <div className="mb-4 flex items-center gap-2">
            <SlidersHorizontal className="size-4 text-muted-foreground" />

            <h2 className="text-sm font-medium">Filter news</h2>

            {hasFilters && (
              <Button
                variant="ghost"
                size="sm"
                className="ml-auto h-8 gap-1.5"
                onClick={clearFilters}
              >
                <X className="size-3.5" />
                Clear filters
              </Button>
            )}
          </div>

          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
            <div className="relative lg:col-span-1">
              <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />

              <Input
                value={searchInput}
                onChange={(event) => setSearchInput(event.target.value)}
                placeholder="Search events..."
                className="pl-9"
              />
            </div>

            <Select
              value={category}
              onValueChange={handleCategoryChange}
              disabled={isCategoriesLoading}
            >
              <SelectTrigger className=" w-full">
                <SelectValue placeholder="All categories">
                  {category === "all"
                    ? "All categories"
                    : (categories.find((item) => item.id === category)?.name ??
                      "Category")}
                </SelectValue>
              </SelectTrigger>

              <SelectContent>
                <SelectItem value="all">All categories</SelectItem>

                {categories.map((item) => (
                  <SelectItem key={item.id} value={item.id}>
                    {item.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Popover>
              <PopoverTrigger
                render={
                  <Button
                    variant="outline"
                    className="w-full justify-start text-left font-normal"
                  >
                    <CalendarIcon className="size-4" />

                    <span
                      className={
                        fromDate ? "text-foreground" : "text-muted-foreground"
                      }
                    >
                      {fromDate ? formatDate(parseDate(fromDate)) : "From date"}
                    </span>
                  </Button>
                }
              ></PopoverTrigger>

              <PopoverContent className="w-auto p-0" align="start">
                <Calendar
                  mode="single"
                  selected={parseDate(fromDate)}
                  onSelect={handleFromDateChange}
                  disabled={(date) =>
                    toDate ? date > parseDate(toDate)! : false
                  }
                />

                {fromDate && (
                  <div className="border-t p-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="w-full"
                      onClick={() => handleFromDateChange(undefined)}
                    >
                      Clear date
                    </Button>
                  </div>
                )}
              </PopoverContent>
            </Popover>

            <Popover>
              <PopoverTrigger
                render={
                  <Button
                    variant="outline"
                    className="w-full justify-start text-left font-normal"
                  >
                    <CalendarIcon className="size-4" />

                    <span
                      className={
                        toDate ? "text-foreground" : "text-muted-foreground"
                      }
                    >
                      {toDate ? formatDate(parseDate(toDate)) : "To date"}
                    </span>
                  </Button>
                }
              ></PopoverTrigger>

              <PopoverContent className="w-auto p-0" align="start">
                <Calendar
                  mode="single"
                  selected={parseDate(toDate)}
                  onSelect={handleToDateChange}
                  disabled={(date) =>
                    fromDate ? date < parseDate(fromDate)! : false
                  }
                />

                {toDate && (
                  <div className="border-t p-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="w-full"
                      onClick={() => handleToDateChange(undefined)}
                    >
                      Clear date
                    </Button>
                  </div>
                )}
              </PopoverContent>
            </Popover>
          </div>
        </section>
      )}

      {(hasEvents || hasFilters) && (
        <div className="mb-4 flex min-h-5 items-center justify-between">
          <p className="text-sm text-muted-foreground">
            {pagination?.total_items ?? 0}{" "}
            {(pagination?.total_items ?? 0) === 1 ? "event" : "events"}
          </p>

          {isFetching && <Spinner className="size-4 text-muted-foreground" />}
        </div>
      )}

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 12 }).map((_, index) => (
            <EventCardSkeleton key={index} />
          ))}
        </div>
      ) : events.length > 0 ? (
        <>
          <div
            className={
              isFetching
                ? "grid gap-4 opacity-60 transition-opacity md:grid-cols-2 xl:grid-cols-3"
                : "grid gap-4 transition-opacity md:grid-cols-2 xl:grid-cols-3"
            }
          >
            {events.map((event) => (
              <EventCard key={event.id} event={event} />
            ))}
          </div>

          {pagination && pagination.total_pages > 1 && (
            <div className="mt-8 flex items-center justify-center gap-2">
              <Button
                variant="outline"
                disabled={!pagination.has_prev || isFetching}
                onClick={() => setPage((current) => current - 1)}
              >
                Previous
              </Button>

              <span className="px-3 text-sm text-muted-foreground">
                Page {pagination.current_page} of {pagination.total_pages}
              </span>

              <Button
                variant="outline"
                disabled={!pagination.has_next || isFetching}
                onClick={() => setPage((current) => current + 1)}
              >
                Next
              </Button>
            </div>
          )}
        </>
      ) : (
        <div className="rounded-xl border py-16 text-center">
          <h2 className="font-semibold">
            {hasFilters ? "No events found" : "No news available"}
          </h2>

          <p className="mt-1 text-sm text-muted-foreground">
            {hasFilters
              ? "Try adjusting your search or filters."
              : "There are no processed news events yet."}
          </p>

          {hasFilters && (
            <Button variant="outline" className="mt-4" onClick={clearFilters}>
              Clear filters
            </Button>
          )}
        </div>
      )}
    </main>
  );
}
