/** Browser-side URL hash (aligned with backend url_deduper for manual ingest). */

export async function urlHash(url) {
  const normalized = url.trim().toLowerCase();
  const data = new TextEncoder().encode(normalized);
  const buf = await crypto.subtle.digest("SHA-256", data);
  return Array.from(new Uint8Array(buf))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}
