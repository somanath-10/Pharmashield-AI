import { z } from "zod";

export const caseRequestSchema = z.object({
  query: z.string().min(20, "Please include a fuller pharmacy case description."),
  drug_name: z.string().min(1),
  payer_name: z.string().min(1),
  patient_context: z.object({
    age: z.number().nullable().optional(),
    diagnoses: z.array(z.string()),
    labs: z.record(z.string()),
    previous_therapies: z.array(z.string()),
    allergies: z.array(z.string())
  }),
  inventory_context: z.object({
    location_id: z.string().nullable().optional(),
    quantity_on_hand: z.number().nullable().optional(),
    reorder_threshold: z.number().nullable().optional(),
    lot_number: z.string().nullable().optional()
  }),
  product_context: z.object({
    supplier_name: z.string().nullable().optional(),
    claim_text: z.string().nullable().optional(),
    ndc: z.string().nullable().optional(),
    lot_number: z.string().nullable().optional(),
    manufacturer: z.string().nullable().optional()
  }),
  denial_letter_text: z.string().nullable().optional()
});
