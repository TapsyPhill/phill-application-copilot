import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import CategoryTabs from "../components/CategoryTabs";
import OpportunityCard from "../components/OpportunityCard";
import { useOpportunities } from "../hooks/useOpportunities";

const TABS = ["All", "Funded", "Email Apply", "Europe", "Manual Review", "High Priority"];

export default function PhdOpportunities() {
  const [tab, setTab] = useState("All");
  const { data, loading, error } = useOpportunities({ category: "phd" });

  const filtered = useMemo(() => {
    let rows = data;
    if (tab === "Funded") {
      rows = rows.filter(
        (o) =>
          (o.funding_status || "").toLowerCase().includes("fund") ||
          (o.summary || "").toLowerCase().match(/funded|stipend|scholarship/),
      );
    }
    if (tab === "Email Apply") {
      rows = rows.filter((o) => o.contact_email || (o.summary || "").toLowerCase().includes("email"));
    }
    if (tab === "Europe") {
      rows = rows.filter((o) =>
        ["EU", "Europe", "Germany", "UK", "Netherlands", "Switzerland"].some((c) =>
          (o.country || "").includes(c),
        ),
      );
    }
    if (tab === "Manual Review") rows = rows.filter((o) => o.status === "manual_review");
    if (tab === "High Priority") rows = rows.filter((o) => (o.final_score || 0) >= 70);
    return rows;
  }, [data, tab]);

  return (
    <div>
      <h2>PhD Opportunities</h2>
      <p className="muted">Funded doctoral and research positions with evidence.</p>
      <CategoryTabs tabs={TABS} active={tab} onChange={setTab} />
      {loading && <p className="muted">Loading…</p>}
      {error && <p className="error-text">{String(error)}</p>}
      {!loading && filtered.length === 0 && (
        <div className="empty-state">
          No PhD opportunities in this filter yet. Add a known PhD URL through <strong>Manual Ingest</strong>, or let the automatic discovery run.
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
