"use client";

import { createContext, useCallback, useContext, useMemo } from "react";
import { useQueryClient } from "@tanstack/react-query";

import {
  removeAccessToken,
  setAccessToken,
  useHasToken,
  useIsHydrated,
} from "@/features/auth/hooks/use-has-token";
import {
  useCurrentUser,
  useLogin,
  useRegister,
} from "@/features/auth/hooks/use-auth";
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User,
} from "@/features/auth/types";

const CURRENT_USER_QUERY_KEY = ["auth", "me"];

type AuthContextValue = {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const queryClient = useQueryClient();

  const hasToken = useHasToken();
  const isHydrated = useIsHydrated();

  const loginMutation = useLogin();
  const registerMutation = useRegister();
  const currentUserQuery = useCurrentUser(hasToken);

  const user = currentUserQuery.data ?? null;

  const login = useCallback(
    async (data: LoginRequest) => {
      const response: TokenResponse = await loginMutation.mutateAsync(data);

      setAccessToken(response.access_token);

      const result = await currentUserQuery.refetch();

      if (!result.data) {
        throw new Error("Failed to retrieve current user");
      }
    },
    [loginMutation, currentUserQuery],
  );

  const register = useCallback(
    async (data: RegisterRequest) => {
      const response = await registerMutation.mutateAsync(data);

      setAccessToken(response.token.access_token);

      const result = await currentUserQuery.refetch();

      if (!result.data) {
        throw new Error("Failed to retrieve current user");
      }
    },
    [registerMutation, currentUserQuery],
  );

  const logout = useCallback(() => {
    removeAccessToken();

    queryClient.removeQueries({
      queryKey: CURRENT_USER_QUERY_KEY,
    });
  }, [queryClient]);

  const isLoading = !isHydrated || (hasToken && currentUserQuery.isLoading);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: user !== null,
      isLoading,
      login,
      register,
      logout,
    }),
    [user, isLoading, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuthContext() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuthContext must be used within AuthProvider");
  }

  return context;
}
