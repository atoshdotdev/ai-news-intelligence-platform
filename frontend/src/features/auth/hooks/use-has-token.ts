"use client";

import { useSyncExternalStore } from "react";

const ACCESS_TOKEN_KEY = "access_token";

const listeners = new Set<() => void>();

export function getAccessToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

function getHasTokenSnapshot(): boolean {
  return getAccessToken() !== null;
}

function getHasTokenServerSnapshot(): boolean {
  return false;
}

function subscribe(listener: () => void): () => void {
  listeners.add(listener);

  const handleStorage = (event: StorageEvent) => {
    if (event.key === ACCESS_TOKEN_KEY) {
      listener();
    }
  };

  window.addEventListener("storage", handleStorage);

  return () => {
    listeners.delete(listener);
    window.removeEventListener("storage", handleStorage);
  };
}

export function useHasToken(): boolean {
  return useSyncExternalStore(
    subscribe,
    getHasTokenSnapshot,
    getHasTokenServerSnapshot,
  );
}

function subscribeHydration(): () => void {
  return () => {};
}

function getHydrationSnapshot(): boolean {
  return true;
}

function getHydrationServerSnapshot(): boolean {
  return false;
}

export function useIsHydrated(): boolean {
  return useSyncExternalStore(
    subscribeHydration,
    getHydrationSnapshot,
    getHydrationServerSnapshot,
  );
}

export function setAccessToken(token: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, token);

  listeners.forEach((listener) => listener());
}

export function removeAccessToken(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY);

  listeners.forEach((listener) => listener());
}
