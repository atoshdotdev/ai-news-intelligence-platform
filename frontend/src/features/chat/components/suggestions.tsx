"use client";

import { Button } from "@/components/ui/button";

const suggestions = [
  {
    label: "Latest tech news",
    prompt:
      "What are the latest important developments in technology and artificial intelligence?",
  },
  {
    label: "Major world events",
    prompt:
      "What are the most important recent developments in international news and world affairs?",
  },
  {
    label: "Latest US news",
    prompt:
      "What are the most important recent developments in the United States?",
  },
  {
    label: "Latest Europe news",
    prompt: "What are the most important recent developments in Europe?",
  },
  {
    label: "Recent conflicts",
    prompt:
      "What are the latest significant developments in major international conflicts and wars?",
  },
  {
    label: "Recent disasters",
    prompt:
      "What major natural disasters or other large-scale disasters have happened recently?",
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
