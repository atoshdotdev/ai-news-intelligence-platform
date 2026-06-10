export type ChatRole = "user" | "assistant";

export type ChatMessage = {
  id: string;
  role: ChatRole;
  content: string;
  sources?: ChatSource[];
};

export type ChatResponse = {
  answer: string;
  sources?: {
    title: string;
    url: string;
  }[];
};

export type ChatSource = {
  title: string;
  url: string;
};
