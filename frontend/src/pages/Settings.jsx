import { useState } from "react";
import { supabase } from "../services/supabaseClient";
import { urlHash } from "../utils/urlHash";

export default function Settings() {
  const [manualUrl, setManualUrl] = useState("");
  const [msg, setMsg] = useState("");

  async function ingestUrl(e) {
    e.preventDefault();
    if (!supabase || !manualUrl.trim()) return;
    const url = manualUrl.trim();
    const hash = await urlHash(url);
    const payload = {
      url,
      url_hash: hash,
      discovery_method: "manual_dashboard",
      status: "pending",
    };
    const { error } = await supabase.from("discovered_urls").upsert(payload, { onConflict: "url_hash" });
    setMsg(error ? error.message : "URL queued for next scrape run.");
    setManualUrl("");
  }

  return (
    <div>
      <h2>Manual Ingest</h2>
      <p className="muted">
        Add a specific opportunity URL when you find one outside the automatic discovery pipeline.
      </p>
      <section>
        <h3>Queue a URL for scraping</h3>
        <form onSubmit={ingestUrl} className="note-row">
          <input
            type="url"
            placeholder="https://…"
            value={manualUrl}
            onChange={(e) => setManualUrl(e.target.value)}
            required
          />
          <button type="submit">Queue URL</button>
        </form>
        {msg && <p className="muted">{msg}</p>}
        <p className="muted small">
          Queued links are scraped during the next pipeline run, then cleaned, classified, scored, and shown in the right dashboard section.
        </p>
      </section>
      <section className="application-panel">
        <h3>Run a fresh round now</h3>
        <p className="muted">
          To immediately run discovery, scraping, cleaning, deduplication, AI analysis, and scoring from this machine:
        </p>
        <code>python scripts/run_opportunity_round.py</code>
        <p className="muted small">
          In GitHub Actions, run the <strong>Daily Scrape</strong> workflow manually. It now executes the full round, not just scraping.
        </p>
      </section>
    </div>
  );
}
