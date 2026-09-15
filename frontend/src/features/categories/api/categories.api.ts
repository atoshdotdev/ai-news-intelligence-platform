import { request } from "@/lib/request";

import type { CategoriesResponse } from "@/features/categories/types";

export const categoriesApi = {
  list: (): Promise<CategoriesResponse> =>
    request({
      url: "/categories",
      method: "GET",
    }),
};
