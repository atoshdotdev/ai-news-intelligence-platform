export type Event = {
  id: string;
  title: string | null;
  summary: string | null;
  category: string | null;
  image_url: string | null;
  last_published_at: string | null;
  article_count: number;
};

export type EventArticle = {
  id: string;
  title: string;
  url: string;
  source_name: string;
  published_at: string | null;
  image_url: string | null;
};

export type EventEntity = {
  label: string;
  value: string;
};

export type EventDetail = {
  id: string;
  title: string | null;
  summary: string | null;
  category: string | null;
  image_url: string | null;
  entities: EventEntity[] | null;
  last_published_at: string | null;
  articles: EventArticle[];
};

export type EventsResponse = {
  items: Event[];
  pagination: {
    total_items: number;
    total_pages: number;
    current_page: number;
    page_size: number;
    has_next: boolean;
    has_prev: boolean;
  };
};

export type UseEventsParams = {
  page?: number;
  size?: number;
  category?: string;
  search?: string;
  from_date?: string;
  to_date?: string;
};
