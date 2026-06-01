import { z } from "zod";

export const sourceSchema = z.object({
  name: z.string().min(2, "Name is required"),
  url: z.url("Please enter a valid URL"),
  selector: z.string().optional(),
});

export type SourceFormValues = z.infer<typeof sourceSchema>;
