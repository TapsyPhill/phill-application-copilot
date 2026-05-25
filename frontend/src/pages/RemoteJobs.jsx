import { Link } from "react-router-dom";
import OpportunityCard from "../components/OpportunityCard";
import { useOpportunities } from "../hooks/useOpportunities";

export default function RemoteJobs() {
  const { data, loading, error } = useOpportunities({ category: "remote_job" });
  return (
    <div>
      <h2>Remote Jobs</h2>
      <p className="muted">Worldwide, EU, and Africa-friendly remote roles.</p>
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
