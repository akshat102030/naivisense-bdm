import { useMemo, useState } from 'react';
import { Section, GroupPill } from '../components/ui';
import { data, GROUPS } from '../data';
import type { Child } from '../data/types';
import { cap, inr, n1, n2 } from '../lib/format';

type SortKey = 'code' | 'group' | 'fees' | 'progress' | 'valueIndex' | 'attendance' | 'improvement' | 'outstanding';

const COLS: { key: SortKey; label: string; left?: boolean }[] = [
  { key: 'code', label: 'Child' },
  { key: 'group', label: 'Group', left: true },
  { key: 'fees', label: 'Fees' },
  { key: 'progress', label: 'Progress' },
  { key: 'valueIndex', label: 'Value index' },
  { key: 'attendance', label: 'Attendance' },
  { key: 'improvement', label: 'Improvement' },
  { key: 'outstanding', label: 'Outstanding' },
];

const uniq = (f: (c: Child) => string) => [...new Set(data.children.map(f))].sort();

export function Explorer({ onSelect }: { onSelect: (code: string) => void }) {
  const [q, setQ] = useState('');
  const [group, setGroup] = useState('');
  const [sev, setSev] = useState('');
  const [inv, setInv] = useState('');
  const [dx, setDx] = useState('');
  const [risk, setRisk] = useState(false);
  const [sort, setSort] = useState<{ key: SortKey; dir: 1 | -1 }>({ key: 'valueIndex', dir: -1 });

  const rows = useMemo(() => {
    const f = data.children.filter(
      (c) =>
        (!q || c.code.toLowerCase().includes(q.trim().toLowerCase())) &&
        (!group || c.group === group) &&
        (!sev || c.severity === sev) &&
        (!inv || c.involvement === inv) &&
        (!dx || c.diagnosis === dx) &&
        (!risk || c.churnRisk),
    );
    return f.sort((a, b) => {
      const av = a[sort.key];
      const bv = b[sort.key];
      return (
        (typeof av === 'number' && typeof bv === 'number' ? av - bv : String(av).localeCompare(String(bv))) * sort.dir
      );
    });
  }, [q, group, sev, inv, dx, risk, sort]);

  const toggleSort = (key: SortKey) =>
    setSort((s) =>
      s.key === key ? { key, dir: s.dir === 1 ? -1 : 1 } : { key, dir: key === 'code' || key === 'group' ? 1 : -1 },
    );
  const ariaSort = (key: SortKey) => (sort.key === key ? (sort.dir === 1 ? 'ascending' : 'descending') : 'none');

  return (
    <Section
      id="explorer"
      eyebrow="Explorer"
      title="Look up any child"
      lead="Children appear by code only. Filter, sort, and open a profile with the score history, risk change, goals and alerts."
    >
      <div className="filters">
        <input
          className="field search"
          type="search"
          placeholder="Search by code, e.g. C014"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          aria-label="Search by child code"
        />
        <select className="field" value={group} onChange={(e) => setGroup(e.target.value)} aria-label="Value group">
          <option value="">All groups</option>
          {GROUPS.map((g) => (
            <option key={g}>{g}</option>
          ))}
        </select>
        <select className="field" value={sev} onChange={(e) => setSev(e.target.value)} aria-label="Severity">
          <option value="">All severities</option>
          {uniq((c) => c.severity).map((s) => (
            <option key={s} value={s}>
              {cap(s)}
            </option>
          ))}
        </select>
        <select className="field" value={inv} onChange={(e) => setInv(e.target.value)} aria-label="Parent involvement">
          <option value="">All involvement</option>
          {['low', 'medium', 'high'].map((s) => (
            <option key={s} value={s}>
              {cap(s)} involvement
            </option>
          ))}
        </select>
        <select className="field" value={dx} onChange={(e) => setDx(e.target.value)} aria-label="Diagnosis">
          <option value="">All diagnoses</option>
          {uniq((c) => c.diagnosis).map((s) => (
            <option key={s}>{s}</option>
          ))}
        </select>
        <label className="field" style={{ display: 'inline-flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
          <input type="checkbox" checked={risk} onChange={(e) => setRisk(e.target.checked)} /> Churn risk only
        </label>
      </div>
      <div className="table-wrap scroll-y">
        <table className="data">
          <thead>
            <tr>
              {COLS.map((c) => (
                <th key={c.key} className={c.left ? 'l' : undefined} aria-sort={ariaSort(c.key)} scope="col">
                  <button type="button" onClick={() => toggleSort(c.key)}>
                    {c.label}
                    <span aria-hidden="true">{sort.key === c.key ? (sort.dir === 1 ? '▲' : '▼') : ''}</span>
                  </button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((c) => (
              <tr
                key={c.code}
                tabIndex={0}
                onClick={() => onSelect(c.code)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') onSelect(c.code);
                }}
              >
                <td style={{ fontWeight: 700 }}>{c.code}</td>
                <td className="l">
                  <GroupPill group={c.group} />
                </td>
                <td>{inr(c.fees)}</td>
                <td>{n1(c.progress)}</td>
                <td style={{ fontWeight: 750 }}>{n2(c.valueIndex)}×</td>
                <td>{c.attendance}%</td>
                <td>+{c.improvement}</td>
                <td>{c.outstanding ? inr(c.outstanding) : '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="count-note">
        Showing {rows.length} of {data.children.length} children.
      </p>
    </Section>
  );
}
