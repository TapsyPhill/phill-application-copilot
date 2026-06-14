import ScoreBadge from "./ScoreBadge";
import StatusBadge from "./StatusBadge";

export default function OpportunityCard({ opportunity }) {
  const o = opportunity;
  const summary = o.summary ? `${o.summary.slice(0, 160)}${o.summary.length > 160 ? "…" : ""}` : "";
  const fundingStatus = o.phd_opportunity_details?.funding_status;
  const contactEmail = validEmail(o.contact_email) ? o.contact_email : null;
  return (
    <article className="opp-card">
      <div className="opp-card-header">
        <ScoreBadge score={o.final_score} />
        <StatusBadge status={o.status} />
        {o.viewed && <span className="badge viewed-badge">Viewed</span>}
        {o.application_status === "submitted" && <span className="badge applied-badge">Applied</span>}
      </div>
      <h3>{o.title}</h3>
      <p className="muted">
        {o.organization || "—"} · {[o.city, o.country].filter(Boolean).join(", ") || "—"}
      </p>
      <div className="card-facts">
        {contactEmail && <span>Email apply: {contactEmail}</span>}
        {o.deadline && <span>Deadline: {o.deadline}</span>}
        {o.application_method && o.application_method !== "unknown" && <span>Method: {o.application_method}</span>}
        {fundingStatus && fundingStatus !== "unclear" && <span>Funding: {fundingStatus}</span>}
      </div>
      {summary && <p className="summary">{summary}</p>}
    </article>
  );
}

function validEmail(value) {
  if (value === true || value === false || value == null) return false;
  const text = String(value).trim();
  if (!text || ["true", "false", "unknown", "unclear", "null", "undefined"].includes(text.toLowerCase())) {
    return false;
  }
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(text);
}
