"use client";

import { Button } from "@/components/ui/button";

const suggestions = [
  {
    label: "What’s in the news today?",
    prompt: "What are the most important news stories right now?",
  },
  {
    label: "Explain a major story",
    prompt:
      "What are the most important details about a major recent news story?",
  },
  {
    label: "Compare news coverage",
    prompt:
      "Compare how different news sources are covering the same major story.",
  },
  {
    label: "What’s trending?",
    prompt: "What news topics and events are currently trending?",
  },
  {
    label: "Summarize recent events",
    prompt:
      "Summarize the most important recent events and explain why they matter.",
  },
  {
    label: "Find related stories",
    prompt:
      "Find recent news stories that are related to the most important events in the news.",
  },
];

export function Suggestions({
  onSelect,
}: {
  onSelect: (prompt: string) => void;
}) {
  return (
    <div className="flex flex-wrap justify-center gap-2">
      {suggestions.map((suggestion) => (
        <Button
          key={suggestion.label}
          variant="outline"
          size="sm"
          onClick={() => onSelect(suggestion.prompt)}
        >
          {suggestion.label}
        </Button>
      ))}
    </div>
  );
}
