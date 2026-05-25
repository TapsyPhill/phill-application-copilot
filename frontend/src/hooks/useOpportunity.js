import { useCallback, useEffect, useState } from "react";
import { supabase } from "../services/supabaseClient";

export function useOpportunity(id) {
  const [opp, setOpp] = useState(null);
  const [evidence, setEvidence] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const reload = useCallback(async () => {
    if (!supabase || !id) return;
    setLoading(true);
    const { data: row, error: err } = await supabase
      .from("opportunities")
      .select("*")
      .eq("id", id)
      .single();
    const { data: ev } = await supabase
      .from("opportunity_evidence")
      .select("*")
      .eq("opportunity_id", id)
      .order("created_at", { ascending: false });
    setOpp(row);
    setEvidence(ev || []);
    setError(err?.message || null);
    setLoading(false);
  }, [id]);

  useEffect(() => {
    reload();
  }, [reload]);

  return { opp, evidence, loading, error, reload };
}
