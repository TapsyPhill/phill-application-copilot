import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "../services/supabaseClient";
import { getAuthRedirectUrl } from "../utils/authRedirect";

const DEFAULT_EMAIL = "phillmhembere@gmail.com";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState(DEFAULT_EMAIL);
  const [password, setPassword] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState("password");

  async function handlePasswordLogin(e) {
    e.preventDefault();
    if (!supabase) {
      setError("Supabase is not configured. Set VITE_SUPABASE_URL and VITE_SUPABASE_PUBLISHABLE_KEY.");
      return;
    }
    setLoading(true);
    setError("");
    const { error: err } = await supabase.auth.signInWithPassword({
      email: email.trim(),
      password,
    });
    setLoading(false);
    if (err) setError(err.message);
    else navigate("/", { replace: true });
  }

  async function handleMagicLink(e) {
    e.preventDefault();
    if (!supabase) {
      setError("Supabase is not configured.");
      return;
    }
    setLoading(true);
    setError("");
    const redirectTo = getAuthRedirectUrl();
    const { error: err } = await supabase.auth.signInWithOtp({
      email: email.trim(),
      options: { emailRedirectTo: redirectTo },
    });
    setLoading(false);
    if (err) setError(err.message);
    else setSent(true);
  }

  return (
    <div className="login-page">
      <div className="login-card login-card-wide">
        <h1>Opportunity Command Center</h1>
        <p className="muted">Private dashboard — sign in to continue.</p>

        <div className="login-tabs">
          <button
            type="button"
            className={mode === "password" ? "tab active" : "tab"}
            onClick={() => {
              setMode("password");
              setSent(false);
              setError("");
            }}
          >
            Email & password
          </button>
          <button
            type="button"
            className={mode === "magic" ? "tab active" : "tab"}
            onClick={() => {
              setMode("magic");
              setSent(false);
              setError("");
            }}
          >
            Magic link
          </button>
        </div>

        {mode === "password" ? (
          <form onSubmit={handlePasswordLogin}>
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="username"
              required
            />
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />
            {error && <p className="error-text">{error}</p>}
            <button type="submit" disabled={loading}>
              {loading ? "Signing in…" : "Sign in"}
            </button>
          </form>
        ) : sent ? (
          <p>Check your email for the sign-in link. It should open the Cloudflare site, not localhost.</p>
        ) : (
          <form onSubmit={handleMagicLink}>
            <label htmlFor="magic-email">Email</label>
            <input
              id="magic-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <p className="muted small">
              Redirect after click: {getAuthRedirectUrl()}
            </p>
            {error && <p className="error-text">{error}</p>}
            <button type="submit" disabled={loading}>
              {loading ? "Sending…" : "Send magic link"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
