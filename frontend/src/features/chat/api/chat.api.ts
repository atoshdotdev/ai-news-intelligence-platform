import { request } from "@/lib/request";
import type { Chat, ChatDetail } from "@/features/chat/types";

export const chatApi = {
  getChats: (): Promise<Chat[]> =>
    request({
      url: "/chat",
      method: "GET",
    }),

  getChat: (chatId: string): Promise<ChatDetail> =>
    request({
      url: `/chat/${chatId}`,
      method: "GET",
    }),

  togglePin: (chatId: string): Promise<Chat> =>
    request({
      url: `/chat/${chatId}/pin`,
      method: "PATCH",
    }),

  deleteChat: (chatId: string): Promise<void> =>
    request({
      url: `/chat/${chatId}`,
      method: "DELETE",
    }),
};
