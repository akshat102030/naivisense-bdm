import { useMemo, useState } from 'react';
import { Scatter, type Point } from '../components/charts/Scatter';
import { Card, GroupPill, Section, Seg } from '../components/ui';
import { data, GROUPS, GROUP_COLOR, GROUP_HINT } from '../data';
import type { Group } from '../data/types';
import { inr, n2 } from '../lib/format';

export function ValueMap({ selected, onSelect }: { selected: string | null; onSelect: (code: string) => void }) {
  const [filter, setFilter] = useState<Group | 'All'>('All');
  const q = data.quadrants;
  const points: Point[] = useMemo(
    () =>
      data.children
        .filter((c) => filter === 'All' || c.group === filter)
        .map((c) => ({
          id: c.code,
          x: c.fees,
          y: c.progress,
          color: GROUP_COLOR[c.group],
          r: 4 + c.sessions / 32,
          selected: c.code === selected,
          tip: (
            <>
              <b>{c.code}</b> · {c.group}
              <br />
              {inr(c.fees)} fees · {c.progress} pts · index {n2(c.valueIndex)}
            </>
          ),
        })),
    [filter, selected],
  );
  const under = data.children.filter((c) => c.group === 'Under-served').sort((a, b) => a.valueIndex - b.valueIndex);
  const top = [...data.children].sort((a, b) => b.valueIndex - a.valueIndex).slice(0, 5);

  return (
    <Section
      id="value-map"
      eyebrow="Q2 · Value map"
      title="Who is thriving, and who is paying for progress they are not getting?"
      alt
      lead={
        <>
          <b>{q.Thriving}</b> children are Thriving, <b>{q.Efficient}</b> Efficient, <b>{q['Under-served']}</b>{' '}
          Under-served and <b>{q['At-risk']}</b> At-risk. Groups split at the median fee ({inr(data.meta.medianFee)})
          and the median progress ({data.meta.medianProgress.toFixed(1)} points). Click a dot for the child&apos;s
          profile.
        </>
      }
    >
      <div className="grid-2">
        <Card>
          <Seg<Group | 'All'>
            label="Filter by value group"
            value={filter}
            onChange={setFilter}
            options={[
              { value: 'All', label: `All ${data.meta.students}` },
              ...GROUPS.map((g) => ({ value: g, label: `${g} ${q[g]}`, color: GROUP_COLOR[g] })),
            ]}
          />
          <Scatter
            height={400}
            points={points}
            xTitle="Fees paid (₹ thousand)"
            yTitle="Progress points"
            xFormat={(v) => `${Math.round(v / 1000)}k`}
            ariaLabel="Scatter of fees paid against progress points for each child, coloured by value group, with dashed median lines"
            medianX={data.meta.medianFee}
            medianY={data.meta.medianProgress}
            onSelect={onSelect}
          />
          <p className="count-note">
            Dot size is sessions attended. Fees form columns because each therapy plan has a fixed monthly price.
          </p>
        </Card>
        <div className="stack">
          <Card title="Review first: Under-served" sub={`${GROUP_HINT['Under-served']}. Lowest value index first.`}>
            <ul className="rank">
              {under.map((c) => (
                <li key={c.code}>
                  <button type="button" onClick={() => onSelect(c.code)}>
                    <span className="code">{c.code}</span>
                    <span className="meta">
                      {inr(c.fees)} · {c.attendance}% attended
                    </span>
                    <span className="vi" style={{ color: 'var(--c-under)' }}>
                      {n2(c.valueIndex)}×
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          </Card>
          <Card title="Best value" sub="Highest value index.">
            <ul className="rank">
              {top.map((c) => (
                <li key={c.code}>
                  <button type="button" onClick={() => onSelect(c.code)}>
                    <span className="code">{c.code}</span>
                    <span className="meta">
                      <GroupPill group={c.group} />
                    </span>
                    <span className="vi" style={{ color: 'var(--c-efficient)' }}>
                      {n2(c.valueIndex)}×
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          </Card>
        </div>
      </div>
    </Section>
  );
}
