import { useState } from "react";
import { useParams } from "react-router-dom";
import EvidencePanel from "../components/EvidencePanel";
import ScoreBadge from "../components/ScoreBadge";
import ScoreBreakdown from "../components/ScoreBreakdown";
import Stage2Actions from "../components/Stage2Actions";
import { useOpportunity } from "../hooks/useOpportunity";
import {
  addNote,
  approveForApplication,
  checkOutOpportunity,
  markDuplicate,
  markApplied,
  markInterested,
  markReviewed,
  markViewed,
  markWrongCategory,
  rejectOpportunity,
  saveOpportunity,
} from "../services/opportunityActions";

export default function OpportunityDetail() {
  const { id } = useParams();
  const { opp, evidence, scores, contacts, details, loading, error, reload } = useOpportunity(id);
  const [note, setNote] = useState("");
  const [msg, setMsg] = useState("");

  async function act(fn) {
    setMsg("");
    const result = await fn(id);
    if (result?.error) {
      setMsg(`Error: ${result.error}`);
      return;
    }
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
      <section className="application-panel">
        <h3>Application Route</h3>
        <div className="application-grid">
          <Info label="Method" value={opp.application_method} />
          <Info label="Email" value={opp.contact_email} href={opp.contact_email ? `mailto:${opp.contact_email}` : null} />
          <Info label="Phone" value={opp.contact_phone} />
          <Info label="Deadline" value={opp.deadline} />
          <Info label="Application URL" value={opp.application_url} href={opp.application_url} />
          <Info label="Funding" value={details?.funding_status} />
          <Info label="Application Status" value={opp.application_status || opp.status} />
        </div>
        {details?.email_proof && (
          <p className="proof-snippet">
            <strong>Email proof:</strong> {details.email_proof}
          </p>
        )}
        {details?.deadline_proof && (
          <p className="proof-snippet">
            <strong>Deadline proof:</strong> {details.deadline_proof}
          </p>
        )}
        {Array.isArray(opp.required_documents) && opp.required_documents.length > 0 && (
          <p className="muted">Required documents: {opp.required_documents.join(", ")}</p>
        )}
        {contacts.length > 0 && (
          <div>
            <h4>Extracted Contacts</h4>
            <ul className="contact-list">
              {contacts.map((contact) => (
                <li key={`${contact.contact_type}-${contact.contact_value}`}>
                  <strong>{contact.contact_type}:</strong> {contact.contact_value}
                  {contact.proof_snippet ? <span className="muted"> — {contact.proof_snippet}</span> : null}
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>
      <section>
        <h3>Score breakdown</h3>
        <ScoreBreakdown scores={scores} />
      </section>
      <section>
        <h3>Evidence</h3>
        <EvidencePanel evidence={evidence} />
      </section>
      <section>
        <h3>Actions</h3>
        <div className="action-row">
          <button type="button" className="primary-action" onClick={() => act(markReviewed)}>
            Mark Reviewed
          </button>
          <button type="button" className="primary-action" onClick={() => act(saveOpportunity)}>
            Save
          </button>
          <button type="button" className="primary-action" onClick={() => act(approveForApplication)}>
            Approve to Apply
          </button>
          <button type="button" className="primary-action" onClick={() => act(markApplied)}>
            Mark Applied
          </button>
          <button type="button" onClick={() => act(rejectOpportunity)}>
            Reject
          </button>
          <button type="button" onClick={() => act(checkOutOpportunity)}>
            Check Out
          </button>
          <button type="button" onClick={() => act(markViewed)}>
            Mark Viewed
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
              const result = await addNote(id, note.trim());
              if (result?.error) {
                setMsg(`Error: ${result.error}`);
                return;
              }
              setNote("");
              setMsg("Note saved.");
            }}
          >
            Add note
          </button>
        </div>
        {msg && <p className={msg.startsWith("Error:") ? "error-text" : "muted"}>{msg}</p>}
        <Stage2Actions />
      </section>
    </div>
  );
}

function Info({ label, value, href }) {
  if (!value || value === "unknown" || value === "unclear") return null;
  return (
    <div className="info-item">
      <span className="muted">{label}</span>
      {href ? (
        <a href={href} target={href.startsWith("mailto:") ? undefined : "_blank"} rel="noreferrer">
          {value}
        </a>
      ) : (
        <strong>{value}</strong>
      )}
    </div>
  );
}
