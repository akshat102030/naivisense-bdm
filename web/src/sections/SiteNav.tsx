import { useActiveSection } from '../hooks/useActiveSection';
import { IDS, NAV } from './nav';

export function SiteNav({ theme, onToggleTheme }: { theme: 'light' | 'dark'; onToggleTheme: () => void }) {
  const active = useActiveSection(IDS);
  return (
    <header className="nav">
      <div className="wrap">
        <nav className="nav-bar" aria-label="Sections">
          <a className="brand" href="#top" aria-label="NaiviSense Outcome Value, back to top">
            <img src="/assets/naivisense-logo-160.png" alt="" width={28} height={28} />
            <span>
              NaiviSense <small>Outcome Value</small>
            </span>
          </a>
          <div className="nav-links">
            {NAV.map((n) => (
              <a key={n.id} className="nav-link" href={`#${n.id}`} aria-current={active === n.id}>
                {n.label}
              </a>
            ))}
          </div>
          <button
            type="button"
            className="icon-btn"
            onClick={onToggleTheme}
            aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
          >
            {theme === 'dark' ? (
              <svg
                width="17"
                height="17"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                aria-hidden="true"
              >
                <circle cx="12" cy="12" r="4" />
                <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
              </svg>
            ) : (
              <svg
                width="17"
                height="17"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
              </svg>
            )}
          </button>
        </nav>
      </div>
    </header>
  );
}
