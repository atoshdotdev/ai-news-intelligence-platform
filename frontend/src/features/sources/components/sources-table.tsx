import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { ExternalLinkIcon, PencilIcon, TrashIcon } from "lucide-react";
import { type Source } from "@/features/sources/types";
import { Spinner } from "@/components/ui/spinner";

type SourcesTableProps = {
  sources: Source[];
  loading: boolean;
  onEdit: (source: Source) => void;
  onDelete: (source: Source) => void;
};

export function SourcesTable({
  sources,
  loading,
  onEdit,
  onDelete,
}: SourcesTableProps) {
  if (loading) {
    return (
      <div className="flex justify-center text-center py-10">
        <Spinner className="size-6" />
      </div>
    );
  }

  if (!sources?.length) {
    return (
      <div className="text-center text-muted-foreground py-10 border rounded-lg">
        No sources found
      </div>
    );
  }

  return (
    <div className="border rounded-lg">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>URL</TableHead>
            <TableHead>Selector</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>

        <TableBody>
          {sources.map((s) => (
            <TableRow key={s.id}>
              <TableCell className="font-medium">{s.name}</TableCell>

              <TableCell className="max-w-64 truncate">
                <a
                  href={s.url}
                  target="_blank"
                  className="flex items-center gap-1 hover:underline"
                >
                  {s.url}
                  <ExternalLinkIcon className="size-3" />
                </a>
              </TableCell>

              <TableCell className="font-medium max-w-64 truncate">
                {s.selector}
              </TableCell>

              <TableCell className="text-right">
                <Button variant="ghost" size="icon" onClick={() => onEdit(s)}>
                  <PencilIcon className="size-4" />
                </Button>
                <Button
                  variant="destructive"
                  size="icon"
                  onClick={() => onDelete(s)}
                >
                  <TrashIcon className="size-4" />
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
