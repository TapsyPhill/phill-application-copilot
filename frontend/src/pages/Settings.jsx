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
      <h2>Settings</h2>
      <p className="muted">Domain: {import.meta.env.VITE_PROJECT_DOMAIN || "not set"}</p>
      <section>
        <h3>Manual URL ingest</h3>
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
      </section>
    </div>
  );
}
