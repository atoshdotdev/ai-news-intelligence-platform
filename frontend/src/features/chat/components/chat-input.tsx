"use client";

import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ArrowUpIcon } from "lucide-react";

export function ChatInput({
  onSend,
  isLoading,
}: {
  onSend: (text: string) => void;
  isLoading?: boolean;
}) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  const handleSend = async () => {
    if (!value.trim()) return;

    const text = value;
    setValue("");
    await onSend(text);

    textareaRef.current?.focus();
  };

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;

    el.style.height = "0px";
    el.style.height = Math.min(el.scrollHeight, 200) + "px";
  }, [value]);

  return (
    <div className="w-full bg-background px-4 py-3">
      <div className="relative max-w-3xl mx-auto">
        <Textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Ask anything..."
          className="resize-none pr-12 py-3 min-h-13 max-h-50 rounded-2xl border shadow-sm focus-visible:ring-1"
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
        />

        <Button
          size="icon"
          className="absolute right-2 bottom-2 rounded-xl h-9 w-9"
          onClick={handleSend}
          disabled={isLoading}
        >
          <ArrowUpIcon className="size-4" />
        </Button>
      </div>
    </div>
  );
}
