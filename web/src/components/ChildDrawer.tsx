import { useEffect, useRef } from 'react';
import { data } from '../data';
import { GroupPill } from './ui';
import { cap, inr, nice, n1, n2 } from '../lib/format';

const NOTE = {
  Thriving: 'Keep the current plan. High fees are matched by high progress.',
  Efficient: 'Strong value for the fees paid. Check whether a higher-intensity plan would speed progress further.',
  'Under-served': 'Review the therapy plan. Fees are above the median but progress is below it.',
  'At-risk': 'Re-engage the family. Both fees and progress are below the median.',
} as const;

export function ChildDrawer({ code, onClose }: { code: string; onClose: () => void }) {
  const closeRef = useRef<HTMLButtonElement>(null);
  const c = data.children.find((x) => x.code === code);

  useEffect(() => {
    closeRef.current?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      window.removeEventListener('keydown', onKey);
      document.body.style.overflow = prev;
    };
  }, [onClose]);

  if (!c) return null;
  const hi = Math.max(c.initialScore, c.latestScore);
  return (
    <div className="overlay" onClick={onClose}>
      <aside
        className="drawer"
        role="dialog"
        aria-modal="true"
        aria-label={`Profile of child ${c.code}`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="drawer-head">
          <div>
            <h3>{c.code}</h3>
            <p className="sub" style={{ margin: '4px 0 10px', color: 'var(--theme-text-muted)', fontSize: 14 }}>
              {c.diagnosis} · {cap(c.severity)} · age {c.ageYears} · {cap(c.involvement)} parent involvement
            </p>
            <GroupPill group={c.group} />
            {c.churnRisk && (
              <span className="pill" style={{ background: 'var(--c-under)', marginLeft: 6 }}>
                Churn risk
              </span>
            )}
          </div>
          <button ref={closeRef} type="button" className="icon-btn" onClick={onClose} aria-label="Close profile">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.2"
              strokeLinecap="round"
              aria-hidden="true"
            >
              <path d="M6 6l12 12M18 6L6 18" />
            </svg>
          </button>
        </div>
        <dl className="kv">
          <div>
            <dt>Value index</dt>
            <dd>{n2(c.valueIndex)}×</dd>
          </div>
          <div>
            <dt>Progress points</dt>
            <dd>{n1(c.progress)}</dd>
          </div>
          <div>
            <dt>Fees paid</dt>
            <dd>{inr(c.fees)}</dd>
          </div>
          <div>
            <dt>Attendance</dt>
            <dd>{c.attendance}%</dd>
          </div>
          <div>
            <dt>Goals completed</dt>
            <dd>
              {c.goalsCompleted} of {c.goalsTotal}
            </dd>
          </div>
          <div>
            <dt>Home tasks a week</dt>
            <dd>{n1(c.homeTasksPerWeek)}</dd>
          </div>
          <div>
            <dt>Alerts (open)</dt>
            <dd>
              {c.alerts} ({c.openAlerts})
            </dd>
          </div>
          <div>
            <dt>Outstanding</dt>
            <dd>{c.outstanding ? inr(c.outstanding) : 'None'}</dd>
          </div>
        </dl>
        <h4 style={{ margin: '0 0 2px', fontSize: 14 }}>Assessment score</h4>
        <div
          className="track"
          role="img"
          aria-label={`Overall score from ${n1(c.initialScore)} to ${n1(c.latestScore)}`}
        >
          <div className="from" style={{ width: `${(c.initialScore / Math.max(hi, 1)) * 100}%` }} />
          <div className="to" style={{ width: `${(c.latestScore / Math.max(hi, 1)) * 100}%`, opacity: 0.85 }} />
        </div>
        <p style={{ margin: '0 0 18px', fontSize: 13, color: 'var(--theme-text-muted)' }}>
          {n1(c.initialScore)} → {n1(c.latestScore)} (+{c.improvement}) · risk band {c.initialRisk} → {c.latestRisk}
        </p>
        <p style={{ margin: '0 0 14px', fontSize: 13.5, color: 'var(--theme-text-secondary)' }}>
          Therapies: {c.therapies.map(nice).join(', ')}
        </p>
        <div className="note">{NOTE[c.group]}</div>
      </aside>
    </div>
  );
}
