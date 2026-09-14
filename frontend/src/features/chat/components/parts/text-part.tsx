import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { type TextMessagePart } from "@/features/chat/tools";

export function TextPart({ part }: { part: TextMessagePart }) {
  if (!part.text.trim()) {
    return null;
  }

  return (
    <div className="prose prose-sm prose-invert max-w-none px-1.5">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{part.text}</ReactMarkdown>
    </div>
  );
}
