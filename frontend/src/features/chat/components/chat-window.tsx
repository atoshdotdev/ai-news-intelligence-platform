"use client";

import { cn } from "@/lib/utils";
import type { ChatMessage } from "@/features/chat/types";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export function ChatWindow({ messages }: { messages: ChatMessage[] }) {
  return (
    <div className="px-4 py-6 space-y-6 max-w-3xl mx-auto w-full">
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={cn(
            "flex w-full",
            msg.role === "user" ? "justify-end" : "justify-start",
          )}
        >
          <div
            className={cn(
              "max-w-[75%] rounded-2xl px-4 py-3 text-sm",
              msg.role === "user"
                ? "bg-primary text-primary-foreground"
                : "bg-muted",
            )}
          >
            {/* <div className="prose prose-sm dark:prose-invert max-w-none wrap-break-word">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {msg.content}
              </ReactMarkdown>
            </div> */}
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {msg.content}
            </ReactMarkdown>

            {msg.sources?.length ? (
              <div className="mt-3 border-t pt-2 space-y-1">
                <p className="text-xs text-muted-foreground">Sources</p>

                <div className="flex flex-col gap-1">
                  {msg.sources.map((source) => (
                    <a
                      key={source.url}
                      href={source.url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-xs text-muted-foreground hover:underline truncate"
                    >
                      {source.title}
                    </a>
                  ))}
                </div>
              </div>
            ) : null}
          </div>
        </div>
      ))}
    </div>
  );
}
