import { chatApi } from "@/features/chat/api/chat.api";

export function useChat() {
  return {
    sendMessage: chatApi.stream,
  };
}
