import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import CategoryTabs from "../components/CategoryTabs";
import OpportunityCard from "../components/OpportunityCard";
import { useOpportunities } from "../hooks/useOpportunities";

const TABS = ["All", "Worldwide", "EU-friendly", "Africa-friendly", "US-only flagged", "High Priority"];

export default function RemoteJobs() {
  const [tab, setTab] = useState("All");
  const { data, loading, error } = useOpportunities({ category: "remote_job" });

  const filtered = useMemo(() => {
    let rows = data;
    const summary = (o) => `${o.summary || ""} ${o.remote_status || ""}`.toLowerCase();
    if (tab === "Worldwide") {
      rows = rows.filter((o) => summary(o).match(/worldwide|global|anywhere|no restriction/));
    }
    if (tab === "EU-friendly") {
      rows = rows.filter((o) => summary(o).match(/eu|europe|emea/));
    }
    if (tab === "Africa-friendly") {
      rows = rows.filter((o) => summary(o).match(/africa|south africa|global south/));
    }
    if (tab === "US-only flagged") {
      rows = rows.filter((o) => summary(o).match(/us only|usa only|united states only/));
    }
    if (tab === "High Priority") rows = rows.filter((o) => (o.final_score || 0) >= 70);
    return rows;
  }, [data, tab]);

  return (
    <div>
      <h2>Remote Jobs</h2>
      <p className="muted">Worldwide, EU, and Africa-friendly remote roles.</p>
      <CategoryTabs tabs={TABS} active={tab} onChange={setTab} />
      {loading && <p className="muted">Loading…</p>}
      {error && <p className="error-text">{String(error)}</p>}
      {!loading && filtered.length === 0 && (
        <div className="empty-state">
          No remote jobs in this filter yet. Add a known remote role through <strong>Manual Ingest</strong>, or let the automatic discovery run.
        </div>
      )}
      <div className="card-list">
        {filtered.map((o) => (
          <Link key={o.id} to={`/opportunity/${o.id}`}>
            <OpportunityCard opportunity={o} />
          </Link>
        ))}
      </div>
    </div>
  );
}
