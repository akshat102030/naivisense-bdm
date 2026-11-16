import type { ReactNode } from 'react';
import { GROUP_COLOR } from '../data';
import type { Group } from '../data/types';

export function Section({
  id,
  eyebrow,
  title,
  lead,
  alt,
  children,
}: {
  id: string;
  eyebrow: string;
  title: string;
  lead?: ReactNode;
  alt?: boolean;
  children: ReactNode;
}) {
  return (
    <section
      id={id}
      className={'band' + (alt ? ' alt' : '')}
      aria-labelledby={`${id}-title`}
      style={{ scrollMarginTop: 72 }}
    >
      <div className="wrap">
        <div className="sec-head">
          <span className="eyebrow">
            <span className="dot" />
            {eyebrow}
          </span>
          <h2 id={`${id}-title`}>{title}</h2>
          {lead && <p>{lead}</p>}
        </div>
        {children}
      </div>
    </section>
  );
}

export function Card({ title, sub, children }: { title?: string; sub?: ReactNode; children: ReactNode }) {
  return (
    <div className="card">
      {title && <h3>{title}</h3>}
      {sub && <p className="sub">{sub}</p>}
      {children}
    </div>
  );
}

export function Seg<T extends string>({
  options,
  value,
  onChange,
  label,
}: {
  options: { value: T; label: string; color?: string }[];
  value: T;
  onChange: (v: T) => void;
  label: string;
}) {
  return (
    <div className="seg" role="group" aria-label={label}>
      {options.map((o) => (
        <button key={o.value} type="button" aria-pressed={value === o.value} onClick={() => onChange(o.value)}>
          {o.color && <span className="sw" style={{ background: o.color }} />}
          {o.label}
        </button>
      ))}
    </div>
  );
}

export function Legend({ items }: { items: { label: string; color: string }[] }) {
  return (
    <div className="legend">
      {items.map((i) => (
        <span key={i.label}>
          <i style={{ background: i.color }} />
          {i.label}
        </span>
      ))}
    </div>
  );
}

export function GroupPill({ group }: { group: Group }) {
  return (
    <span className="pill" style={{ background: GROUP_COLOR[group] }}>
      {group}
    </span>
  );
}

export function Stat({ value, label }: { value: ReactNode; label: string }) {
  return (
    <div className="stat">
      <div className="v">{value}</div>
      <div className="l">{label}</div>
    </div>
  );
}
