export default function StatusBadge({ status }) {
  return <span className={`badge status status-${status}`}>{status}</span>;
}
