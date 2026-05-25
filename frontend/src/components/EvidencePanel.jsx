export default function EvidencePanel({ evidence = [] }) {
  if (!evidence.length) {
    return <p className="muted">No evidence snippets stored yet.</p>;
  }
  return (
    <ul className="evidence-list">
      {evidence.map((e) => (
        <li key={e.id}>
          <strong>{e.evidence_type}</strong>
          <blockquote>{e.snippet}</blockquote>
        </li>
      ))}
    </ul>
  );
}
