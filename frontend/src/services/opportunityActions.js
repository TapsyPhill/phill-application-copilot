import { supabase } from "./supabaseClient";

export async function recordAction(opportunityId, actionType, payload = {}) {
  if (!supabase) return { error: "Supabase not configured" };
  await supabase.from("opportunity_user_actions").insert({
    opportunity_id: opportunityId,
    action_type: actionType,
    action_payload: payload,
  });
}

export async function updateOpportunityStatus(opportunityId, status, extra = {}) {
  if (!supabase) return { error: "Supabase not configured" };
  const { data: existing } = await supabase
    .from("opportunities")
    .select("status")
    .eq("id", opportunityId)
    .single();
  await supabase
    .from("opportunities")
    .update({ status, ...extra })
    .eq("id", opportunityId);
  await supabase.from("opportunity_status_history").insert({
    opportunity_id: opportunityId,
    old_status: existing?.status,
    new_status: status,
    changed_by: "user",
  });
  return { ok: true };
}

export async function markViewed(opportunityId) {
  return updateOpportunityStatus(opportunityId, "reviewing", {
    viewed: true,
    viewed_at: new Date().toISOString(),
    last_opened_at: new Date().toISOString(),
  });
}

export async function saveOpportunity(opportunityId) {
  await recordAction(opportunityId, "save");
  return updateOpportunityStatus(opportunityId, "saved");
}

export async function rejectOpportunity(opportunityId) {
  await recordAction(opportunityId, "reject");
  return updateOpportunityStatus(opportunityId, "rejected");
}

export async function markInterested(opportunityId) {
  await recordAction(opportunityId, "mark_interested");
  return updateOpportunityStatus(opportunityId, "saved");
}

export async function markWrongCategory(opportunityId) {
  await recordAction(opportunityId, "wrong_category");
  return updateOpportunityStatus(opportunityId, "manual_review");
}

export async function markDuplicate(opportunityId) {
  await recordAction(opportunityId, "mark_duplicate");
  return updateOpportunityStatus(opportunityId, "archived");
}

export async function addNote(opportunityId, noteText) {
  if (!supabase) return { error: "Supabase not configured" };
  await supabase.from("opportunity_notes").insert({
    opportunity_id: opportunityId,
    note_text: noteText,
  });
  await recordAction(opportunityId, "note", { text: noteText });
  return { ok: true };
}
