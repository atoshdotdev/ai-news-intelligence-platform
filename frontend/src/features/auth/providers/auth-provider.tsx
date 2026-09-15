"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from "react";
import { useQueryClient } from "@tanstack/react-query";

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

const ACCESS_TOKEN_KEY = "access_token";
const CURRENT_USER_QUERY_KEY = ["auth", "me"];

type AuthContextValue = {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<User>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const queryClient = useQueryClient();

  const [hasToken, setHasToken] = useState<boolean | null>(() => {
    if (typeof window === "undefined") {
      return null;
    }

    return localStorage.getItem(ACCESS_TOKEN_KEY) !== null;
  });

  const loginMutation = useLogin();
  const registerMutation = useRegister();
  const currentUserQuery = useCurrentUser(hasToken === true);

  const user = currentUserQuery.data ?? null;

  const login = useCallback(
    async (data: LoginRequest) => {
      const response: TokenResponse = await loginMutation.mutateAsync(data);

      localStorage.setItem(ACCESS_TOKEN_KEY, response.access_token);

      setHasToken(true);

      const result = await currentUserQuery.refetch();

      if (!result.data) {
        throw new Error("Failed to retrieve current user");
      }
    },
    [loginMutation, currentUserQuery],
  );

  const register = useCallback(
    async (data: RegisterRequest): Promise<User> => {
      return registerMutation.mutateAsync(data);
    },
    [registerMutation],
  );

  const logout = useCallback(() => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);

    setHasToken(false);

    queryClient.removeQueries({
      queryKey: CURRENT_USER_QUERY_KEY,
    });
  }, [queryClient]);

  const isLoading =
    hasToken === null || (hasToken === true && currentUserQuery.isLoading);

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

export { ACCESS_TOKEN_KEY };
