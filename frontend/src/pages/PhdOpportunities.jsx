import { Link } from "react-router-dom";
import OpportunityCard from "../components/OpportunityCard";
import { useOpportunities } from "../hooks/useOpportunities";

export default function PhdOpportunities() {
  const { data, loading, error } = useOpportunities({ category: "phd" });
  return (
    <div>
      <h2>PhD Opportunities</h2>
      <p className="muted">Funded doctoral and research positions with evidence.</p>
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
