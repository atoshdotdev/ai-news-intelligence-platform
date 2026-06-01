import api from "./api-client";

type RequestOptions = {
  method?: "GET" | "POST" | "PUT" | "DELETE" | "PATCH";
  url: string;
  data?: any;
  params?: any;
};

export async function request<T>({
  method = "GET",
  url,
  data,
  params,
}: RequestOptions): Promise<T> {
  const res = await api.request<T>({
    method,
    url,
    data,
    params,
  });

  return res.data;
}
