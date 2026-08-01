import { ChatSource } from "@/features/chat/types";

export const chatApi = {
  stream: async (
    message: string,
    callbacks: {
      onToken: (token: string) => void;
      onSources: (sources: ChatSource[]) => void;
      onDone: () => void;
      onError?: (error: string) => void;
    },
  ) => {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });

    if (!res.body) {
      callbacks.onError?.("No response body from server");
      callbacks.onDone();
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();

    let buffer = "";

    try {
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        const parts = buffer.split("\n\n");
        buffer = parts.pop() || "";

        for (const part of parts) {
          const line = part.trim();

          if (!line.startsWith("data:")) continue;

          const raw = line.replace("data: ", "");

          let json;
          try {
            json = JSON.parse(raw);
          } catch (e) {
            console.error("Failed to parse SSE chunk:", raw);
            continue;
          }

          switch (json.type) {
            case "sources":
              callbacks.onSources(json.sources);
              break;

            case "token":
              callbacks.onToken(json.content);
              break;

            case "error":
              callbacks.onError?.(json.message);
              break;

            case "done":
              callbacks.onDone();
              break;
          }
        }
      }
    } catch (err: any) {
      callbacks.onError?.(err?.message || "Stream failed");
    } finally {
      callbacks.onDone();
    }
  },
};
