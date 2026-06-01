"use client";

import { useParams } from "next/navigation";

import { useSource } from "@/features/sources/hooks/use-sources";
import { SourceBlacklistManager } from "@/features/sources/components/source-blacklist-manager";
import { Spinner } from "@/components/ui/spinner";
import { ExternalLinkIcon } from "lucide-react";

export default function SourceDetailPage() {
  const params = useParams();
  const sourceId = params.id as string;

  const { data: source } = useSource(sourceId);

  if (!source) {
    return (
      <div className="flex justify-center text-center py-10">
        <Spinner className="size-6" />
      </div>
    );
  }

  return (
    <div className="w-full max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">{source.name}</h1>
        <a
          href={source.url}
          target="_blank"
          className="w-fit flex items-center gap-1 hover:underline text-sm text-muted-foreground"
        >
          {source.url}
          <ExternalLinkIcon className="size-3" />
        </a>
      </div>

      <div className="border rounded-lg p-4">
        <SourceBlacklistManager sourceId={source.id} />
      </div>
    </div>
  );
}
