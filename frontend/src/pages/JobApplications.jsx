import { Link } from "react-router-dom";
import OpportunityCard from "../components/OpportunityCard";
import { useOpportunities } from "../hooks/useOpportunities";

export default function JobApplications() {
  const { data, loading, error } = useOpportunities({ category: "job" });
  return (
    <div>
      <h2>Job Applications</h2>
      <p className="muted">Germany/EU data, ML, and LLM-aligned roles.</p>
      {loading && <p className="muted">Loading…</p>}
      {error && <p className="error-text">{String(error)}</p>}
      <div className="card-list">
        {data.map((o) => (
          <Link key={o.id} to={`/opportunity/${o.id}`}>
            <OpportunityCard opportunity={o} />
          </Link>
        ))}
      </div>
    </div>
  );
}
