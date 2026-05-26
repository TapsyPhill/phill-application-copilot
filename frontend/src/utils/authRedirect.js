/** Production redirect for Supabase magic links (avoids localhost:3000 from dashboard Site URL). */

export function getAuthRedirectUrl() {
  const explicit = import.meta.env.VITE_AUTH_REDIRECT_URL;
  if (explicit) {
    return explicit.endsWith("/") ? explicit : `${explicit}/`;
  }

  const domain = (import.meta.env.VITE_PROJECT_DOMAIN || "").trim();
  if (domain) {
    const host = domain.replace(/^https?:\/\//, "").replace(/\/$/, "");
    const isLocal = host.includes("localhost") || host.startsWith("127.0.0.1");
    return `${isLocal ? "http" : "https"}://${host}/`;
  }

  return `${window.location.origin}/`;
}
