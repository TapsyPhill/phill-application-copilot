import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import CategoryTabs from "../components/CategoryTabs";
import OpportunityCard from "../components/OpportunityCard";
import { useOpportunities } from "../hooks/useOpportunities";

const TABS = ["All", "Germany", "EU", "Email Apply", "Manual Review", "High Priority"];

export default function JobApplications() {
  const [tab, setTab] = useState("All");
  const { data, loading, error } = useOpportunities({ category: "job" });

  const filtered = useMemo(() => {
    let rows = data;
    if (tab === "Germany") rows = rows.filter((o) => (o.country || "").includes("Germany"));
    if (tab === "EU") {
      rows = rows.filter((o) =>
        ["EU", "Europe", "Germany", "Netherlands", "France", "Spain"].some((c) =>
          (o.country || "").includes(c),
        ),
      );
    }
    if (tab === "Email Apply") {
      rows = rows.filter((o) => o.contact_email || (o.application_method || "").toLowerCase().includes("email"));
    }
    if (tab === "Manual Review") rows = rows.filter((o) => o.status === "manual_review");
    if (tab === "High Priority") rows = rows.filter((o) => (o.final_score || 0) >= 70);
    return rows;
  }, [data, tab]);

  return (
    <div>
      <h2>Job Applications</h2>
      <p className="muted">Germany/EU data, ML, and LLM-aligned roles.</p>
      <CategoryTabs tabs={TABS} active={tab} onChange={setTab} />
      {loading && <p className="muted">Loading…</p>}
      {error && <p className="error-text">{String(error)}</p>}
      {!loading && filtered.length === 0 && (
        <div className="empty-state">
          No job opportunities in this filter yet. Add a known job URL through <strong>Manual Ingest</strong>, or let the automatic discovery run.
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
