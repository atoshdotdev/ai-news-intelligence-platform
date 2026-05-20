"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

import { SourcesTable } from "@/features/sources/components/sources-table";
import { SourceModal } from "@/features/sources/components/sources-modal";
import { useSources } from "@/features/sources/hooks/use-sources";
import { Source } from "@/features/sources/types";
import { Pagination } from "@/components/pagination";
// import { SearchBar } from "@/components/SearchBar";

export default function SourcesPage() {
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<Source | null>(null);

  const [page, setPage] = useState(1);
  const [size] = useState(10);

  const { data, isLoading, refetch } = useSources({
    page,
    size,
  });

  const sources = data?.data ?? [];
  const metadata = data?.metadata;

  const totalPages = metadata?.total_pages ?? 1;

  return (
    <div className="w-full max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Sources</h1>
          <p className="text-sm text-muted-foreground">
            Manage ingestion sources for your AI pipeline
          </p>
        </div>

        <Button
          onClick={() => {
            setEditing(null);
            setOpen(true);
          }}
        >
          <Plus className="size-4 mr-2" />
          Add Source
        </Button>
      </div>

      {/* <SearchBar /> */}

      <div className="space-y-4">
        <SourcesTable
          sources={sources}
          loading={isLoading}
          onEdit={(source) => {
            setEditing(source);
            setOpen(true);
          }}
        />

        <Pagination
          page={page}
          totalPages={totalPages}
          onPageChange={setPage}
        />
      </div>

      <SourceModal
        open={open}
        onOpenChange={setOpen}
        initialData={editing}
        onSuccess={() => {
          setOpen(false);
          setEditing(null);
          refetch();
        }}
      />
    </div>
  );
}
