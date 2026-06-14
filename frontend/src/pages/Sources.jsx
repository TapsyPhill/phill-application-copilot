import { useEffect, useState } from "react";
import { getSupabaseConfigError, supabase } from "../services/supabaseClient";

export default function Sources() {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(getSupabaseConfigError());

  useEffect(() => {
    const configError = getSupabaseConfigError();
    if (configError) {
      setError(configError);
      setLoading(false);
      return;
    }
    supabase
      .from("sources")
      .select("id,source_name,url,target_section,enabled,health_score,country")
      .order("priority", { ascending: false })
      .limit(200)
      .then(({ data, error: queryError }) => {
        if (queryError) {
          setError(queryError.message);
          setSources([]);
        } else {
          setSources(data || []);
          setError(null);
        }
        setLoading(false);
      });
  }, []);

  return (
    <div>
      <h2>Sources</h2>
      <p className="muted">Registry of discovery/scrape sources and health scores.</p>
      {error && <p className="error-text">{error}</p>}
      {loading && <p className="muted">Loading…</p>}
      {!loading && !error && sources.length === 0 && (
        <p className="muted">No sources found. Run `python scripts/seed_sources.py` to populate the registry.</p>
      )}
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
