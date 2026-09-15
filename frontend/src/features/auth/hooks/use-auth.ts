"use client";

import { useMutation, useQuery } from "@tanstack/react-query";

import { authApi } from "@/features/auth/api/auth.api";
import { useAuthContext } from "@/features/auth/providers/auth-provider";

export function useAuth() {
  return useAuthContext();
}

export function useLogin() {
  return useMutation({
    mutationFn: authApi.login,
  });
}

export function useRegister() {
  return useMutation({
    mutationFn: authApi.register,
  });
}

export function useCurrentUser(enabled: boolean) {
  return useQuery({
    queryKey: ["auth", "me"],
    queryFn: authApi.getMe,
    enabled,
    retry: false,
  });
}
