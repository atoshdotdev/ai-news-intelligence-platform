import { type UIDataTypes, type UIMessage } from "ai";
import { ChatMessage } from "../types";

export type ChatUIMessage = UIMessage<unknown, UIDataTypes>;

export type ChatMessagePart = ChatUIMessage["parts"][number];

export type TextMessagePart = Extract<ChatMessagePart, { type: "text" }>;

export type SourceUrlPart = Extract<ChatMessagePart, { type: "source-url" }>;

export function toUIMessage(messages: ChatMessage[]): UIMessage[] {
  return messages.map((message) => ({
    id: message.id,
    role: message.role as ChatUIMessage["role"],
    parts: [
      {
        type: "text",
        text: message.content,
      },
    ],
  }));
}
