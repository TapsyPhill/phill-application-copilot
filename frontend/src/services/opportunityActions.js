import { supabase } from "./supabaseClient";

export async function recordAction(opportunityId, actionType, payload = {}) {
  if (!supabase) return { error: "Supabase not configured" };
  const { error } = await supabase.from("opportunity_user_actions").insert({
    opportunity_id: opportunityId,
    action_type: actionType,
    action_payload: payload,
  });
  if (error) return { error: error.message };
  return { ok: true };
}

export async function updateOpportunityStatus(opportunityId, status, extra = {}) {
  if (!supabase) return { error: "Supabase not configured" };
  const { data: existing, error: fetchErr } = await supabase
    .from("opportunities")
    .select("status")
    .eq("id", opportunityId)
    .single();
  if (fetchErr) return { error: fetchErr.message };

  const { error: updateErr } = await supabase
    .from("opportunities")
    .update({ status, ...extra })
    .eq("id", opportunityId);
  if (updateErr) return { error: updateErr.message };

  const { error: histErr } = await supabase.from("opportunity_status_history").insert({
    opportunity_id: opportunityId,
    old_status: existing?.status,
    new_status: status,
    changed_by: "user",
  });
  if (histErr) return { error: histErr.message };
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
  const actionResult = await recordAction(opportunityId, "save");
  if (actionResult.error) return actionResult;
  return updateOpportunityStatus(opportunityId, "saved");
}

export async function rejectOpportunity(opportunityId) {
  const actionResult = await recordAction(opportunityId, "reject");
  if (actionResult.error) return actionResult;
  return updateOpportunityStatus(opportunityId, "rejected");
}

export async function markInterested(opportunityId) {
  const actionResult = await recordAction(opportunityId, "mark_interested");
  if (actionResult.error) return actionResult;
  return updateOpportunityStatus(opportunityId, "saved");
}

export async function markWrongCategory(opportunityId) {
  const actionResult = await recordAction(opportunityId, "wrong_category");
  if (actionResult.error) return actionResult;
  return updateOpportunityStatus(opportunityId, "manual_review");
}

export async function markDuplicate(opportunityId) {
  const actionResult = await recordAction(opportunityId, "mark_duplicate");
  if (actionResult.error) return actionResult;
  return updateOpportunityStatus(opportunityId, "archived");
}

export async function addNote(opportunityId, noteText) {
  if (!supabase) return { error: "Supabase not configured" };
  const { error: noteErr } = await supabase.from("opportunity_notes").insert({
    opportunity_id: opportunityId,
    note_text: noteText,
  });
  if (noteErr) return { error: noteErr.message };
  return recordAction(opportunityId, "note", { text: noteText });
}
