import ScoreBadge from "./ScoreBadge";
import StatusBadge from "./StatusBadge";

export default function OpportunityCard({ opportunity }) {
  const o = opportunity;
  const summary = o.summary ? `${o.summary.slice(0, 160)}${o.summary.length > 160 ? "…" : ""}` : "";
  return (
    <article className="opp-card">
      <div className="opp-card-header">
        <ScoreBadge score={o.final_score} />
        <StatusBadge status={o.status} />
        {o.viewed && <span className="badge viewed-badge">Viewed</span>}
      </div>
      <h3>{o.title}</h3>
      <p className="muted">
        {o.organization || "—"} · {[o.city, o.country].filter(Boolean).join(", ") || "—"}
      </p>
      {summary && <p className="summary">{summary}</p>}
    </article>
  );
}
