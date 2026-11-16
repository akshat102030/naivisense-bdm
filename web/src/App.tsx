import { useCallback, useState } from 'react';
import { ChildDrawer } from './components/ChildDrawer';
import { useTheme } from './hooks/useTheme';
import { Alerts } from './sections/Alerts';
import { Domains } from './sections/Domains';
import { Drivers } from './sections/Drivers';
import { Explorer } from './sections/Explorer';
import { Hero } from './sections/Hero';
import { Method } from './sections/Method';
import { Revenue } from './sections/Revenue';
import { SiteNav } from './sections/SiteNav';
import { Therapists } from './sections/Therapists';
import { ValueMap } from './sections/ValueMap';
import { data } from './data';

export function App() {
  const [theme, toggleTheme] = useTheme();
  const [selected, setSelected] = useState<string | null>(null);
  const close = useCallback(() => setSelected(null), []);

  return (
    <>
      <a href="#main-content" className="sr-only">
        Skip to content
      </a>
      <SiteNav theme={theme} onToggleTheme={toggleTheme} />
      <main id="main-content">
        <span id="top" />
        <Hero />
        <Therapists />
        <ValueMap selected={selected} onSelect={setSelected} />
        <Drivers />
        <Domains />
        <Alerts />
        <Revenue onSelect={setSelected} />
        <Explorer onSelect={setSelected} />
        <Method />
      </main>
      <footer className="footer">
        <div className="wrap">
          <span>
            NaiviSense Outcome Value · BDM project · {data.meta.period}. Prepared for Naivedyam Child Development
            Center. Sample data shown; children appear by code only.
          </span>
          <span>Built with React, TypeScript and Vite.</span>
        </div>
      </footer>
      {selected && <ChildDrawer code={selected} onClose={close} />}
    </>
  );
}
