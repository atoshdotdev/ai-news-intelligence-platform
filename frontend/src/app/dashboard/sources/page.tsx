"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

import { SourcesTable } from "@/features/sources/components/sources-table";
import { SourceModal } from "@/features/sources/components/sources-modal";
import { useSources } from "@/features/sources/hooks/use-sources";
import { Source } from "@/features/sources/types";
import { Pagination } from "@/components/pagination";
import { ConfirmDeleteModal } from "@/components/confirm-delete-modal";
import { useDeleteSource } from "@/features/sources/hooks/use-delete-source";

export default function SourcesPage() {
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<Source | null>(null);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [sourceToDelete, setSourceToDelete] = useState<Source | null>(null);
  const deleteSource = useDeleteSource();

  const [page, setPage] = useState(1);
  const [size] = useState(10);

  const { data, isLoading } = useSources({
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

      <div className="space-y-4">
        <SourcesTable
          sources={sources}
          loading={isLoading}
          onEdit={(source) => {
            setEditing(source);
            setOpen(true);
          }}
          onDelete={(source) => {
            setSourceToDelete(source);
            setDeleteModalOpen(true);
          }}
        />

        <Pagination
          page={page}
          totalPages={totalPages}
          hasNext={metadata?.has_next ?? false}
          hasPrev={metadata?.has_prev ?? false}
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
        }}
      />

      <ConfirmDeleteModal
        open={deleteModalOpen}
        onOpenChange={setDeleteModalOpen}
        title="Delete Source"
        description="Are you sure you want to delete this source? This action cannot be undone."
        onConfirm={async () => {
          if (!sourceToDelete) return;

          await deleteSource.mutateAsync(sourceToDelete.id);

          setDeleteModalOpen(false);
          setSourceToDelete(null);
        }}
      />
    </div>
  );
}
