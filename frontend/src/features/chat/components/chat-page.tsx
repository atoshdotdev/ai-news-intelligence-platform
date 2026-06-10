"use client";

import { useEffect, useRef, useState } from "react";
import { ChatWindow } from "@/features/chat/components/chat-window";
import { ChatInput } from "@/features/chat/components/chat-input";
import { useChat } from "@/features/chat/hooks/use-chat";
import type { ChatMessage } from "@/features/chat/types";

export function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const { sendMessage } = useChat();
  const bottomRef = useRef<HTMLDivElement | null>(null);

  const handleSend = async (text: string) => {
    if (isLoading) return;

    setIsLoading(true);

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
    };

    const assistantId = crypto.randomUUID();

    setMessages((prev) => [
      ...prev,
      userMessage,
      { id: assistantId, role: "assistant", content: "" },
    ]);

    let assistantText = "";

    try {
      await sendMessage(text, {
        onToken: (token) => {
          assistantText += token;

          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, content: assistantText } : m,
            ),
          );
        },

        onSources: (sources) => {
          setMessages((prev) =>
            prev.map((m) => (m.id === assistantId ? { ...m, sources } : m)),
          );
        },

        onDone: () => {
          setIsLoading(false);
        },
      });
    } catch (err) {
      console.error(err);
      setIsLoading(false);
    }
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto">
        <ChatWindow messages={messages} />
        <div ref={bottomRef} />
      </div>

      <div className="sticky bottom-0 border-t bg-background">
        <ChatInput onSend={handleSend} isLoading={isLoading} />
      </div>
    </div>
  );
}
