import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import {
  Briefcase,
  ClipboardList,
  Cloud,
  Github,
  LayoutDashboard,
  Search,
  Sparkles,
} from 'lucide-react'
import './styles.css'

const features = [
  {
    icon: Search,
    title: 'Job discovery',
    description: 'Collect and surface job opportunities from configured sources.',
  },
  {
    icon: ClipboardList,
    title: 'Application tracking',
    description: 'Track applications, status, and follow-ups in one place.',
  },
  {
    icon: Github,
    title: 'GitHub workflow',
    description: 'Version control, Actions scheduler, and deployment triggers.',
  },
  {
    icon: Cloud,
    title: 'Cloudflare Pages',
    description: 'Hosted at phill-application-copilot.uk via Git integration.',
  },
]

function App() {
  return (
    <div className="page">
      <header className="hero">
        <div className="hero-badge">
          <Sparkles size={16} aria-hidden />
          <span>Stage 1 — Dashboard setup</span>
        </div>
        <h1>Phill Application Copilot</h1>
        <p className="hero-lead">
          Automated job discovery and application tracking. Stage 1 focuses on
          collecting opportunities, preparing scraping workflows, and
          documenting accounts and API keys. The full dashboard is coming next.
        </p>
        <div className="hero-meta">
          <span className="meta-pill">
            <Briefcase size={14} aria-hidden />
            phill-application-copilot.uk
          </span>
          <span className="meta-pill">
            <LayoutDashboard size={14} aria-hidden />
            Vite + React on Cloudflare Pages
          </span>
        </div>
      </header>

      <main className="content">
        <section className="card-grid" aria-label="Stage 1 capabilities">
          {features.map(({ icon: Icon, title, description }) => (
            <article key={title} className="card">
              <div className="card-icon" aria-hidden>
                <Icon size={22} />
              </div>
              <h2>{title}</h2>
              <p>{description}</p>
            </article>
          ))}
        </section>

        <section className="status-card">
          <h2>What&apos;s live in Stage 1</h2>
          <ul>
            <li>Frontend landing page and Cloudflare Pages build pipeline</li>
            <li>Repository structure for scraping workflows and secrets docs</li>
            <li>Placeholder GitHub Actions workflow (deployment via Pages)</li>
            <li>Stage 2 may add automated job applications later</li>
          </ul>
        </section>
      </main>

      <footer className="footer">
        <p>Phill Application Copilot · Stage 1 repository structure is ready.</p>
      </footer>
    </div>
  )
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
