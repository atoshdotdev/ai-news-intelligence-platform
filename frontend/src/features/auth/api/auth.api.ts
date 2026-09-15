import { request } from "@/lib/request";

import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User,
} from "@/features/auth/types";

export const authApi = {
  getMe: (): Promise<User> =>
    request({
      url: "/auth/me",
      method: "GET",
    }),

  login: (data: LoginRequest): Promise<TokenResponse> =>
    request({
      url: "/auth/login",
      method: "POST",
      data,
    }),

  register: (data: RegisterRequest): Promise<User> =>
    request({
      url: "/auth/register",
      method: "POST",
      data,
    }),
};
