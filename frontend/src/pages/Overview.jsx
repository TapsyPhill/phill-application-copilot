import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { supabase } from "../services/supabaseClient";

export default function Overview() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!supabase) {
      setLoading(false);
      return;
    }
    async function load() {
      const today = new Date().toISOString().slice(0, 10);
      const [all, high, review, client, phd, jobs, remote] = await Promise.all([
        supabase.from("opportunities").select("id", { count: "exact", head: true }),
        supabase.from("opportunities").select("id", { count: "exact", head: true }).gte("final_score", 80),
        supabase
          .from("opportunities")
          .select("id", { count: "exact", head: true })
          .eq("status", "manual_review"),
        supabase
          .from("opportunities")
          .select("id", { count: "exact", head: true })
          .eq("category", "client_lead"),
        supabase.from("opportunities").select("id", { count: "exact", head: true }).eq("category", "phd"),
        supabase.from("opportunities").select("id", { count: "exact", head: true }).eq("category", "job"),
        supabase
          .from("opportunities")
          .select("id", { count: "exact", head: true })
          .eq("category", "remote_job"),
      ]);
      const { count: newToday } = await supabase
        .from("opportunities")
        .select("id", { count: "exact", head: true })
        .gte("first_seen_at", `${today}T00:00:00`);

      setMetrics({
        total: all.count ?? 0,
        newToday: newToday ?? 0,
        high: high.count ?? 0,
        review: review.count ?? 0,
        client: client.count ?? 0,
        phd: phd.count ?? 0,
        jobs: jobs.count ?? 0,
        remote: remote.count ?? 0,
      });
      setLoading(false);
    }
    load();
  }, []);

  const cards = metrics
    ? [
        { label: "Total opportunities", value: metrics.total },
        { label: "New today", value: metrics.newToday },
        { label: "High priority (80+)", value: metrics.high },
        { label: "Manual review", value: metrics.review },
        { label: "Client leads", value: metrics.client },
        { label: "PhD", value: metrics.phd },
        { label: "Jobs", value: metrics.jobs },
        { label: "Remote jobs", value: metrics.remote },
      ]
    : [];

  return (
    <div>
      <h2>Overview</h2>
      <p className="muted">Daily intelligence dashboard — live from Supabase.</p>
      {loading && <p className="muted">Loading metrics…</p>}
      <div className="metrics-grid">
        {cards.map((m) => (
          <div key={m.label} className="metric-card">
            <span className="metric-value">{m.value}</span>
            <span className="metric-label">{m.label}</span>
          </div>
        ))}
      </div>
      <p className="muted" style={{ marginTop: "1.5rem" }}>
        <Link to="/review">Review queue</Link> · <Link to="/sources">Sources</Link> ·{" "}
        <Link to="/settings">Settings</Link>
      </p>
    </div>
  );
}
