"use client";

import { useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  type SourceFormValues,
  sourceSchema,
} from "@/features/sources/schemas/source.schema";
import { useCreateSource } from "@/features/sources/hooks/use-create-source";
import { useUpdateSource } from "@/features/sources/hooks/use-update-source";
import { Source } from "@/features/sources/types";

type SourceModalProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  initialData?: Source | null;
  onSuccess: () => void;
};

export function SourceModal({
  open,
  onOpenChange,
  initialData,
  onSuccess,
}: SourceModalProps) {
  const isEdit = !!initialData;

  const createSource = useCreateSource();
  const updateSource = useUpdateSource();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(sourceSchema),
    defaultValues: {
      source_name: "",
      source_url: "",
    },
  });

  useEffect(() => {
    if (initialData) {
      reset({
        source_name: initialData.source_name,
        source_url: initialData.source_url,
      });
    } else {
      reset({
        source_name: "",
        source_url: "",
      });
    }
  }, [initialData, reset]);

  const onSubmit = async (data: SourceFormValues) => {
    if (isEdit) {
      await updateSource.mutateAsync({
        id: initialData.id,
        data,
      });
    } else {
      await createSource.mutateAsync(data);
    }

    onSuccess();
  };

  const isLoading = createSource.isPending || updateSource.isPending;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{isEdit ? "Edit Source" : "Create Source"}</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <Input placeholder="Source name" {...register("source_name")} />
            {errors.source_name && (
              <p className="text-sm text-red-500">
                {errors.source_name.message}
              </p>
            )}
          </div>

          <div>
            <Input placeholder="Source URL" {...register("source_url")} />
            {errors.source_url && (
              <p className="text-sm text-red-500">
                {errors.source_url.message}
              </p>
            )}
          </div>

          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="secondary"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>

            <Button type="submit" disabled={isLoading}>
              {isLoading ? "Saving..." : isEdit ? "Update" : "Create"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
