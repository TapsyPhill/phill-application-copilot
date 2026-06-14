import { useEffect, useState } from "react";
import { getSupabaseConfigError, supabase } from "../services/supabaseClient";

export default function LogsHealth() {
  const [audits, setAudits] = useState([]);
  const [usage, setUsage] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(getSupabaseConfigError());

  useEffect(() => {
    const configError = getSupabaseConfigError();
    if (configError) {
      setError(configError);
      setLoading(false);
      return;
    }
    Promise.all([
      supabase
        .from("audit_logs")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(50),
      supabase
        .from("api_usage_logs")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(50),
    ]).then(([auditResult, usageResult]) => {
      const queryError = auditResult.error?.message || usageResult.error?.message || null;
      if (queryError) {
        setError(queryError);
        setAudits([]);
        setUsage([]);
      } else {
        setAudits(auditResult.data || []);
        setUsage(usageResult.data || []);
        setError(null);
      }
      setLoading(false);
    });
  }, []);

  return (
    <div>
      <h2>Logs & Health</h2>
      {error && <p className="error-text">{error}</p>}
      {loading && <p className="muted">Loading logs…</p>}
      <h3>Audit log</h3>
      {!loading && !error && audits.length === 0 && <p className="muted">No audit entries yet.</p>}
      <ul className="log-list">
        {audits.map((a) => (
          <li key={a.id}>
            {a.created_at} — {a.action} {a.details ? JSON.stringify(a.details) : ""}
          </li>
        ))}
      </ul>
      <h3>API usage</h3>
      {!loading && !error && usage.length === 0 && <p className="muted">No API usage logged yet.</p>}
      <ul className="log-list">
        {usage.map((u) => (
          <li key={u.id}>
            {u.created_at} — {u.service_name} ({u.units_used})
          </li>
        ))}
      </ul>
    </div>
  );
}
