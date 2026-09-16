"use client";

import { Spinner } from "@/components/ui/spinner";
import { ChatContent } from "@/features/chat/components/chat-content";
import { useChatDetail } from "@/features/chat/hooks/use-chat";
import { toUIMessage } from "@/features/chat/tools/index";

type ChatProps = {
  chatId?: string;
};

export function Chat({ chatId }: ChatProps) {
  const { data: chatDetail, isLoading, isError } = useChatDetail(chatId);

  if (chatId && isLoading) {
    return (
      <div className="flex min-h-0 flex-1 items-center justify-center">
        <Spinner className="size-6 text-muted-foreground" />
      </div>
    );
  }

  if (chatId && isError) {
    return (
      <div className="flex min-h-0 flex-1 items-center justify-center">
        <span className="text-sm text-destructive">Failed to load chat.</span>
      </div>
    );
  }

  return (
    <ChatContent
      initialChatId={chatId}
      initialMessages={chatDetail ? toUIMessage(chatDetail.messages) : []}
    />
  );
}
