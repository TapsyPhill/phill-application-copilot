import { useEffect, useState } from "react";
import { supabase } from "../services/supabaseClient";

export default function LogsHealth() {
  const [audits, setAudits] = useState([]);
  const [usage, setUsage] = useState([]);

  useEffect(() => {
    if (!supabase) return;
    supabase
      .from("audit_logs")
      .select("*")
      .order("created_at", { ascending: false })
      .limit(50)
      .then(({ data }) => setAudits(data || []));
    supabase
      .from("api_usage_logs")
      .select("*")
      .order("created_at", { ascending: false })
      .limit(50)
      .then(({ data }) => setUsage(data || []));
  }, []);

  return (
    <div>
      <h2>Logs & Health</h2>
      <h3>Audit log</h3>
      <ul className="log-list">
        {audits.map((a) => (
          <li key={a.id}>
            {a.created_at} — {a.action} {a.details ? JSON.stringify(a.details) : ""}
          </li>
        ))}
      </ul>
      <h3>API usage</h3>
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
