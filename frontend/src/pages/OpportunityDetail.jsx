import { useState } from "react";
import { useParams } from "react-router-dom";
import EvidencePanel from "../components/EvidencePanel";
import ScoreBadge from "../components/ScoreBadge";
import Stage2Actions from "../components/Stage2Actions";
import { useOpportunity } from "../hooks/useOpportunity";
import {
  addNote,
  markDuplicate,
  markInterested,
  markViewed,
  markWrongCategory,
  rejectOpportunity,
  saveOpportunity,
} from "../services/opportunityActions";

export default function OpportunityDetail() {
  const { id } = useParams();
  const { opp, evidence, loading, error, reload } = useOpportunity(id);
  const [note, setNote] = useState("");
  const [msg, setMsg] = useState("");

  async function act(fn) {
    await fn(id);
    setMsg("Saved.");
    await reload();
  }

  if (loading) return <p className="muted">Loading…</p>;
  if (error || !opp) return <p className="error-text">{error || "Not found"}</p>;

  return (
    <div>
      <h2>{opp.title}</h2>
      <p className="muted">
        {opp.category} · {opp.country || "—"} ·{" "}
        <a href={opp.source_url} target="_blank" rel="noreferrer">
          Open original
        </a>
      </p>
      <ScoreBadge score={opp.final_score} />
      <p>{opp.summary}</p>
      <section>
        <h3>Evidence</h3>
        <EvidencePanel evidence={evidence} />
      </section>
      <section>
        <h3>Actions</h3>
        <div className="action-row">
          <button type="button" onClick={() => act(markViewed)}>
            Mark Viewed
          </button>
          <button type="button" onClick={() => act(saveOpportunity)}>
            Save
          </button>
          <button type="button" onClick={() => act(rejectOpportunity)}>
            Reject
          </button>
          <button type="button" onClick={() => act(markInterested)}>
            Mark Interested
          </button>
          <button type="button" onClick={() => act(markWrongCategory)}>
            Wrong Category
          </button>
          <button type="button" onClick={() => act(markDuplicate)}>
            Mark Duplicate
          </button>
        </div>
        <div className="note-row">
          <input
            type="text"
            placeholder="Add note…"
            value={note}
            onChange={(e) => setNote(e.target.value)}
          />
          <button
            type="button"
            onClick={async () => {
              if (!note.trim()) return;
              await addNote(id, note.trim());
              setNote("");
              setMsg("Note saved.");
            }}
          >
            Add note
          </button>
        </div>
        {msg && <p className="muted">{msg}</p>}
        <Stage2Actions />
      </section>
    </div>
  );
}
