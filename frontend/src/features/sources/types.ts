export type Source = {
  id: number;
  source_name: string;
  source_url: string;
  selector?: string | null;
  created_at?: string;
  updated_at?: string;
};

export type CreateSourceDTO = {
  source_name: string;
  source_url: string;
  selector?: string;
};

export type UpdateSourceDTO = CreateSourceDTO;

export type UseSourcesParams = {
  page?: number;
  size?: number;
  search?: string;
};

export type SourcesResponse = {
  data: Source[];
  metadata: {
    current_page: number;
    total_pages: number;
    total: number;
    size: number;
    has_next: boolean;
    has_prev: boolean;
  };
};
