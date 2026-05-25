import { useCallback, useEffect, useState } from "react";
import { fetchOpportunities } from "../services/supabaseClient";

export function useOpportunities(filters = {}) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const reload = useCallback(async () => {
    setLoading(true);
    const { data: rows, error: err } = await fetchOpportunities(filters);
    setData(rows || []);
    setError(err?.message || (typeof err === "string" ? err : null));
    setLoading(false);
  }, [JSON.stringify(filters)]);

  useEffect(() => {
    reload();
  }, [reload]);

  return { data, loading, error, reload };
}
