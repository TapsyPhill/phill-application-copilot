import { createClient } from "@supabase/supabase-js";

const url = import.meta.env.VITE_SUPABASE_URL;
const key = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;

export const supabase = url && key ? createClient(url, key) : null;

export async function fetchOpportunities(filters = {}) {
  if (!supabase) return { data: [], error: "Supabase not configured" };
  let q = supabase.from("opportunities").select("*").order("final_score", { ascending: false });
  if (filters.category) q = q.eq("category", filters.category);
  if (filters.subcategory) q = q.eq("subcategory", filters.subcategory);
  if (filters.viewed !== undefined) q = q.eq("viewed", filters.viewed);
  if (filters.status) q = q.eq("status", filters.status);
  if (filters.country) q = q.eq("country", filters.country);
  if (filters.minScore) q = q.gte("final_score", filters.minScore);
  if (filters.sourceGroup) q = q.ilike("subcategory", `%${filters.sourceGroup}%`);
  return q.limit(filters.limit || 100);
}
