export type ChatRole = "user" | "assistant";

export type ChatMessage = {
  id: string;
  role: ChatRole;
  content: string;
  sources?: ChatSource[];
  created_at: string;
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

export type Chat = {
  id: string;
  title: string;
  pinned: boolean;
  created_at: string;
  updated_at: string;
};

export type ChatDetail = Chat & {
  messages: ChatMessage[];
};
