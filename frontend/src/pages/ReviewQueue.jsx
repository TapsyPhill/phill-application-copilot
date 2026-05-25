import { Link } from "react-router-dom";
import OpportunityCard from "../components/OpportunityCard";
import { useOpportunities } from "../hooks/useOpportunities";

export default function ReviewQueue() {
  const { data, loading, error } = useOpportunities({ status: "manual_review" });
  return (
    <div>
      <h2>Review Queue</h2>
      <p className="muted">Low agreement or uncertain AI classifications.</p>
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
