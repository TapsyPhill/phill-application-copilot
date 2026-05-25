import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { supabase } from "../services/supabaseClient";

const nav = [
  { to: "/", label: "Overview" },
  { to: "/client-leads", label: "Client Leads" },
  { to: "/phd", label: "PhD" },
  { to: "/jobs", label: "Jobs" },
  { to: "/remote", label: "Remote Jobs" },
  { to: "/review", label: "Review Queue" },
  { to: "/sources", label: "Sources" },
  { to: "/profile", label: "Profile" },
  { to: "/logs", label: "Logs" },
  { to: "/settings", label: "Settings" },
];

export default function Layout() {
  const navigate = useNavigate();

  async function signOut() {
    if (supabase) await supabase.auth.signOut();
    navigate("/login");
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h1 className="brand">Opportunity Command Center</h1>
        <p className="brand-sub">Stage 1 · Intelligence & Review</p>
        <nav>
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <button type="button" className="sign-out-btn" onClick={signOut}>
          Sign out
        </button>
      </aside>
      <main className="main">
        <Outlet />
      </main>
    </div>
  );
}
