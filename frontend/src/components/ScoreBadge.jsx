export default function ScoreBadge({ score }) {
  const n = Number(score) || 0;
  const tier = n >= 80 ? "high" : n >= 60 ? "mid" : n >= 40 ? "review" : "low";
  return <span className={`badge score score-${tier}`}>{n.toFixed(0)}</span>;
}
