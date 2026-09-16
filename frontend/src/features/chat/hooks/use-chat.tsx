"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { chatApi } from "@/features/chat/api/chat.api";

export const CHATS_QUERY_KEY = ["chats"];
export const chatQueryKey = (chatId: string) => ["chat", chatId];

export function useChatDetail(chatId: string | undefined) {
  return useQuery({
    queryKey: chatId ? chatQueryKey(chatId) : ["chat", undefined],
    queryFn: () => chatApi.getChat(chatId!),
    enabled: Boolean(chatId),
  });
}

export function useChats() {
  return useQuery({
    queryKey: CHATS_QUERY_KEY,
    queryFn: chatApi.getChats,
  });
}

export function usePinnedChats() {
  const query = useChats();

  return {
    ...query,
    data: query.data?.filter((chat) => chat.pinned) ?? [],
  };
}

export function usePreviousChats() {
  const query = useChats();

  return {
    ...query,
    data: query.data?.filter((chat) => !chat.pinned) ?? [],
  };
}

export function useToggleChatPin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: chatApi.togglePin,
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: CHATS_QUERY_KEY,
      });
    },
  });
}

export function useDeleteChat() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: chatApi.deleteChat,
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: CHATS_QUERY_KEY,
      });
    },
  });
}
