import { z } from "zod";

export const sourceSchema = z.object({
  source_name: z.string().min(2),
  source_url: z.url(),
});

export type SourceFormValues = z.infer<typeof sourceSchema>;
