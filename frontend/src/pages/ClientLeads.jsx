import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import CategoryTabs from "../components/CategoryTabs";
import OpportunityCard from "../components/OpportunityCard";
import { useOpportunities } from "../hooks/useOpportunities";

const TABS = ["Germany", "Global", "South Africa", "Contact Available", "Manual Review", "High Priority"];

const TAB_FILTERS = {
  Germany: { country: "Germany" },
  Global: {},
  "South Africa": { country: "South Africa" },
  "Contact Available": { minScore: 60 },
  "Manual Review": { status: "manual_review" },
  "High Priority": { minScore: 80 },
};

export default function ClientLeads() {
  const [tab, setTab] = useState(TABS[0]);
  const filters = useMemo(
    () => ({ category: "client_lead", ...TAB_FILTERS[tab] }),
    [tab],
  );
  const { data, loading, error } = useOpportunities(filters);

  const filtered = useMemo(() => {
    if (tab === "Global") {
      return data.filter((o) => o.country !== "Germany" && o.country !== "South Africa");
    }
    if (tab === "Contact Available") {
      return data.filter((o) => o.contact_email || o.contact_phone);
    }
    return data;
  }, [data, tab]);

  return (
    <div>
      <h2>Client Leads</h2>
      <p className="muted">
        Technical-service leads: web, apps, AI, automation, data, digitization, APIs, booking systems.
      </p>
      <CategoryTabs tabs={TABS} active={tab} onChange={setTab} />
      {loading && <p className="muted">Loading…</p>}
      {error && <p className="error-text">{String(error)}</p>}
      {!loading && filtered.length === 0 && (
        <div className="empty-state">
          No leads yet. Run <code>python scripts/run_daily_scrape.py</code> after seeding sources.
        </div>
      )}
      <div className="card-list">
        {filtered.map((o) => (
          <Link key={o.id} to={`/opportunity/${o.id}`}>
            <OpportunityCard opportunity={o} />
          </Link>
        ))}
      </div>
    </div>
  );
}
