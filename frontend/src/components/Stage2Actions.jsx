const STAGE2_ACTIONS = [
  "Generate Email",
  "Create Gmail Draft",
  "Prepare Documents",
  "Start Portal Assist",
  "Follow Up",
];

export default function Stage2Actions() {
  return (
    <div className="stage2-actions">
      <p className="muted">Stage 2 — coming after intelligence layer is stable</p>
      {STAGE2_ACTIONS.map((label) => (
        <button key={label} type="button" disabled title="Stage 2 not enabled">
          {label}
        </button>
      ))}
    </div>
  );
}
