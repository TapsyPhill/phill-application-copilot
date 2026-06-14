import { useCallback, useEffect, useState } from "react";
import { getSupabaseConfigError, supabase } from "../services/supabaseClient";

export function useOpportunity(id) {
  const [opp, setOpp] = useState(null);
  const [evidence, setEvidence] = useState([]);
  const [scores, setScores] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const reload = useCallback(async () => {
    if (!id) {
      setLoading(false);
      setError("Missing opportunity id");
      return;
    }
    const configError = getSupabaseConfigError();
    if (configError) {
      setLoading(false);
      setError(configError);
      return;
    }
    setLoading(true);
    setError(null);
    const { data: row, error: err } = await supabase
      .from("opportunities")
      .select("*")
      .eq("id", id)
      .single();
    const { data: ev, error: evErr } = await supabase
      .from("opportunity_evidence")
      .select("*")
      .eq("opportunity_id", id)
      .order("created_at", { ascending: false });
    const { data: scoreRows, error: scoreErr } = await supabase
      .from("opportunity_scores")
      .select("*")
      .eq("opportunity_id", id)
      .order("created_at", { ascending: false })
      .limit(1);
    const queryError = err?.message || evErr?.message || scoreErr?.message || null;
    setOpp(row);
    setEvidence(ev || []);
    setScores((scoreRows && scoreRows[0]) || null);
    setError(queryError);
    setLoading(false);
  }, [id]);

  useEffect(() => {
    reload();
  }, [reload]);

  return { opp, evidence, scores, loading, error, reload };
}
