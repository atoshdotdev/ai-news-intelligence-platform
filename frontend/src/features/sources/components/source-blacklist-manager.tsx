"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import { TrashIcon } from "lucide-react";

import {
  useBlacklist,
  useCreateBlacklist,
  useDeleteBlacklist,
} from "@/features/sources/hooks/use-blacklist";
import { Spinner } from "@/components/ui/spinner";
import { ConfirmDeleteModal } from "@/components/confirm-delete-modal";

import type { BlacklistEntry } from "@/features/sources/types";

export function SourceBlacklistManager({ sourceId }: { sourceId: string }) {
  const [value, setValue] = useState("");
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [blacklistEntryToDelete, setBlacklistEntryToDelete] =
    useState<BlacklistEntry | null>(null);

  const { data: entries = [], isLoading } = useBlacklist(sourceId);
  const createBlacklist = useCreateBlacklist(sourceId);
  const deleteBlacklist = useDeleteBlacklist(sourceId);

  const add = async () => {
    if (!value.trim()) return;

    await createBlacklist.mutateAsync({
      url_fragment: value.trim(),
    });

    setValue("");
  };

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-sm font-semibold">Blacklist</h3>
        <p className="text-xs text-muted-foreground">
          URL fragments excluded from crawling
        </p>
      </div>

      <div className="flex gap-2">
        <Input
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="e.g. politics, sports"
          className="max-w-md"
        />

        <Button type="button" onClick={add}>
          Add
        </Button>
      </div>

      <div className="border rounded-lg">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Fragment</TableHead>
              <TableHead className="text-center w-25">Actions</TableHead>
            </TableRow>
          </TableHeader>

          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={2} className="text-center py-6">
                  <Spinner className="size-6 mx-auto" />
                </TableCell>
              </TableRow>
            ) : entries.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={2}
                  className="text-center text-muted-foreground py-6"
                >
                  No blacklist entries
                </TableCell>
              </TableRow>
            ) : (
              entries.map((e: BlacklistEntry) => (
                <TableRow key={e.id}>
                  <TableCell>{e.url_fragment}</TableCell>

                  <TableCell className="flex justify-center">
                    <Button
                      variant="destructive"
                      size="icon"
                      onClick={() => {
                        setDeleteModalOpen(true);
                        setBlacklistEntryToDelete(e);
                      }}
                    >
                      <TrashIcon className="size-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <ConfirmDeleteModal
        open={deleteModalOpen}
        onOpenChange={setDeleteModalOpen}
        title="Delete Blacklist Entry"
        description="Are you sure you want to delete this blacklist entry? This action cannot be undone."
        onConfirm={async () => {
          if (!blacklistEntryToDelete) return;

          await deleteBlacklist.mutateAsync(blacklistEntryToDelete.id);

          setDeleteModalOpen(false);
          setBlacklistEntryToDelete(null);
        }}
      />
    </div>
  );
}
