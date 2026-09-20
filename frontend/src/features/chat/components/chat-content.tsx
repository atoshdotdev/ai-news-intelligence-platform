"use client";

import { useState } from "react";
import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport } from "ai";

import { ChatMessage } from "@/features/chat/components/chat-message";
import { PromptForm } from "@/features/chat/components/prompt-form";
import { Suggestions } from "@/features/chat/components/suggestions";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Empty,
  EmptyContent,
  EmptyHeader,
  EmptyTitle,
} from "@/components/ui/empty";
import {
  MessageScroller,
  MessageScrollerButton,
  MessageScrollerContent,
  MessageScrollerItem,
  MessageScrollerProvider,
  MessageScrollerViewport,
} from "@/components/ui/message-scroller";
import { getAccessToken } from "@/features/auth/hooks/use-has-token";
import type { UIMessage } from "ai";
import { useQueryClient } from "@tanstack/react-query";
import { CHATS_QUERY_KEY } from "@/features/chat/hooks/use-chat";
import type { Chat as ChatType } from "@/features/chat/types";

type ChatContentProps = {
  initialChatId?: string;
  initialMessages: UIMessage[];
};

type AgentStatus = "searching" | null;

export function ChatContent({
  initialChatId,
  initialMessages,
}: ChatContentProps) {
  const queryClient = useQueryClient();

  const [chatId, setChatId] = useState<string | undefined>(initialChatId);
  const [agentStatus, setAgentStatus] = useState<AgentStatus>(null);

  const { messages, sendMessage, status, stop, error } = useChat({
    messages: initialMessages,

    transport: new DefaultChatTransport({
      api: `${process.env.NEXT_PUBLIC_API_URL}/chat`,

      prepareSendMessagesRequest: ({ messages }) => ({
        body: {
          chat_id: chatId ?? null,
          messages,
        },
      }),

      headers: (): Record<string, string> => {
        const token = getAccessToken();

        if (!token) {
          return {};
        }

        return {
          Authorization: `Bearer ${token}`,
        };
      },
    }),

    onData: (dataPart) => {
      if (
        dataPart.type === "data-chatId" &&
        typeof dataPart.data === "string"
      ) {
        const newChatId = dataPart.data;

        setChatId(newChatId);

        if (!initialChatId) {
          window.history.replaceState(null, "", `/chat/${newChatId}`);

          queryClient.invalidateQueries({
            queryKey: CHATS_QUERY_KEY,
          });
        }
      }

      if (
        dataPart.type === "data-chatTitle" &&
        typeof dataPart.data === "string"
      ) {
        const newTitle = dataPart.data;

        queryClient.setQueryData<ChatType[]>(CHATS_QUERY_KEY, (chats) => {
          if (!chats) return chats;

          return chats.map((chat) =>
            chat.id === chatId
              ? {
                  ...chat,
                  title: newTitle,
                }
              : chat,
          );
        });
      }

      if (
        dataPart.type === "data-agent-status" &&
        typeof dataPart.data === "object" &&
        dataPart.data !== null &&
        "status" in dataPart.data
      ) {
        const agentStatus = dataPart.data.status;

        if (agentStatus === "searching") {
          setAgentStatus("searching");
        } else if (agentStatus === "idle") {
          setAgentStatus(null);
        }
      }
    },

    onFinish: () => {
      setAgentStatus(null);
    },
  });

  const isBusy = status === "submitted" || status === "streaming";

  const lastMessage = messages.at(-1);

  const isStreamingText =
    lastMessage?.role === "assistant" &&
    lastMessage.parts.some(
      (part) => part.type === "text" && part.text.length > 0,
    );

  return (
    <div className="mx-auto flex min-h-0 w-full flex-1 flex-col">
      {messages.length === 0 ? (
        <div className="flex flex-1 items-center justify-center p-6">
          <Empty>
            <EmptyHeader>
              <EmptyTitle>What can I help with?</EmptyTitle>
            </EmptyHeader>

            <EmptyContent>
              <Suggestions
                onSelect={(prompt) => sendMessage({ text: prompt })}
              />
            </EmptyContent>
          </Empty>
        </div>
      ) : (
        <MessageScrollerProvider>
          <MessageScroller className="flex-1">
            <MessageScrollerViewport>
              <MessageScrollerContent className="mx-auto flex w-full max-w-2xl flex-col gap-6 px-6 py-6">
                {messages.map((message) => (
                  <MessageScrollerItem
                    key={message.id}
                    messageId={message.id}
                    scrollAnchor={message.role === "user"}
                  >
                    <ChatMessage
                      message={message}
                      isStreaming={isBusy && message.id === lastMessage?.id}
                    />
                  </MessageScrollerItem>
                ))}

                {isBusy && !isStreamingText && (
                  <MessageScrollerItem messageId="agent-status">
                    <div className="flex shimmer items-center gap-2 px-3 text-sm text-muted-foreground">
                      {agentStatus === "searching"
                        ? "Searching news…"
                        : "Thinking…"}
                    </div>
                  </MessageScrollerItem>
                )}
              </MessageScrollerContent>
            </MessageScrollerViewport>

            <MessageScrollerButton />
          </MessageScroller>
        </MessageScrollerProvider>
      )}

      <div className="mx-auto flex w-full max-w-2xl flex-col gap-2 px-6 pb-6">
        {error && (
          <Alert variant="destructive">
            <AlertTitle>Request failed</AlertTitle>
            <AlertDescription>{error.message}</AlertDescription>
          </Alert>
        )}

        <PromptForm
          isBusy={isBusy}
          onSubmit={(text) => sendMessage({ text })}
          onStop={() => stop()}
        />
      </div>
    </div>
  );
}
