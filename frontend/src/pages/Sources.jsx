import { useEffect, useState } from "react";
import { supabase } from "../services/supabaseClient";

export default function Sources() {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!supabase) return;
    supabase
      .from("sources")
      .select("id,source_name,url,target_section,enabled,health_score,country")
      .order("priority", { ascending: false })
      .limit(200)
      .then(({ data }) => {
        setSources(data || []);
        setLoading(false);
      });
  }, []);

  return (
    <div>
      <h2>Sources</h2>
      <p className="muted">Registry of discovery/scrape sources and health scores.</p>
      {loading && <p className="muted">Loading…</p>}
      <table className="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Section</th>
            <th>Country</th>
            <th>Health</th>
            <th>Enabled</th>
          </tr>
        </thead>
        <tbody>
          {sources.map((s) => (
            <tr key={s.id}>
              <td>
                <a href={s.url} target="_blank" rel="noreferrer">
                  {s.source_name}
                </a>
              </td>
              <td>{s.target_section}</td>
              <td>{s.country || "—"}</td>
              <td>{s.health_score ?? "—"}</td>
              <td>{s.enabled ? "yes" : "no"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
