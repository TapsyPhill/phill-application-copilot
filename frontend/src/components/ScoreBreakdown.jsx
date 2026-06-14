export default function ScoreBreakdown({ scores }) {
  if (!scores) return null;
  const rows = [
    ["Profile match", scores.profile_match_score],
    ["Recency", scores.recency_score],
    ["Evidence", scores.evidence_score],
    ["Contact", scores.contact_score],
    ["Application method", scores.application_method_score],
    ["Country fit", scores.country_score],
    ["Source reliability", scores.source_reliability_score],
    ["Urgency", scores.urgency_score],
    ["Duplicate penalty", scores.duplicate_penalty],
  ].filter(([, v]) => v != null && v !== "");

  if (rows.length === 0) return <p className="muted">No score breakdown stored yet.</p>;

  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>Dimension</th>
          <th>Score</th>
        </tr>
      </thead>
      <tbody>
        {rows.map(([label, value]) => (
          <tr key={label}>
            <td>{label}</td>
            <td>{Number(value).toFixed(1)}</td>
          </tr>
        ))}
        <tr>
          <td>
            <strong>Final</strong>
          </td>
          <td>
            <strong>{Number(scores.final_score ?? 0).toFixed(1)}</strong>
          </td>
        </tr>
      </tbody>
    </table>
  );
}
