"use client";

import { useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import { Button } from "@/components/ui/button";
import { Field, FieldDescription, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import {
  type SourceFormValues,
  sourceSchema,
} from "@/features/sources/schemas/source.schema";

import {
  useCreateSource,
  useUpdateSource,
} from "@/features/sources/hooks/use-sources";

import type { Source } from "@/features/sources/types";

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
  } = useForm<SourceFormValues>({
    resolver: zodResolver(sourceSchema),
    defaultValues: {
      name: "",
      url: "",
      selector: "",
    },
  });

  useEffect(() => {
    if (!initialData) {
      reset({ name: "", url: "", selector: "" });
      return;
    }

    reset({
      name: initialData.name,
      url: initialData.url,
      selector: initialData.selector ?? "",
    });
  }, [initialData, reset]);

  const onSubmit = async (data: SourceFormValues) => {
    if (isEdit && initialData) {
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
          <Field data-invalid={!!errors.name}>
            <FieldLabel>Source Name *</FieldLabel>
            <Input
              id="input-field-name"
              type="text"
              placeholder="Enter source name"
              aria-invalid={!!errors.name}
              {...register("name")}
            />
            {errors.name && (
              <FieldDescription className="text-red-500">
                {errors.name.message}
              </FieldDescription>
            )}
          </Field>

          <Field data-invalid={!!errors.url}>
            <FieldLabel>Source URL *</FieldLabel>
            <Input
              id="input-field-url"
              type="text"
              placeholder="Enter source URL"
              aria-invalid={!!errors.url}
              {...register("url")}
            />
            {errors.url && (
              <FieldDescription className="text-red-500">
                {errors.url.message}
              </FieldDescription>
            )}
          </Field>

          <Field data-invalid={!!errors.selector}>
            <FieldLabel>Selector</FieldLabel>
            <Input
              id="input-field-selector"
              type="text"
              placeholder="Enter selector"
              aria-invalid={!!errors.selector}
              {...register("selector")}
            />
            {errors.selector && (
              <FieldDescription className="text-red-500">
                {errors.selector.message}
              </FieldDescription>
            )}
          </Field>

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
