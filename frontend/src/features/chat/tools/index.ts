import { type UIDataTypes, type UIMessage } from "ai";

export type ChatUIMessage = UIMessage<unknown, UIDataTypes>;

export type ChatMessagePart = ChatUIMessage["parts"][number];

export type TextMessagePart = Extract<ChatMessagePart, { type: "text" }>;

export type SourceUrlPart = Extract<ChatMessagePart, { type: "source-url" }>;
