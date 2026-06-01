export type Source = {
  id: string;
  name: string;
  url: string;
  selector?: string;
};

export type CreateSourceDTO = {
  name: string;
  url: string;
  selector?: string;
};

export type UpdateSourceDTO = CreateSourceDTO;

export type UseSourcesParams = {
  page?: number;
  size?: number;
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

export type BlacklistEntry = {
  id: string;
  url_fragment: string;
  source_id: string;
};

export type CreateBlacklistDTO = {
  url_fragment: string;
};
