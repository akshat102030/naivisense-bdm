import { useState } from 'react';
import { BarChart } from '../components/charts/BarChart';
import { Scatter } from '../components/charts/Scatter';
import { Card, Legend, Section, Seg, Stat } from '../components/ui';
import { data, INVOLVEMENT_COLOR } from '../data';
import { cap, n1, n2, pct } from '../lib/format';

type Key = 'involvement' | 'severity' | 'diagnosis' | 'age' | 'fee';

const TITLES: Record<Key, string> = {
  involvement: 'Parent involvement',
  severity: 'Severity',
  diagnosis: 'Primary diagnosis',
  age: 'Age band',
  fee: 'Monthly fee tier',
};

export function Drivers() {
  const [key, setKey] = useState<Key>('involvement');
  const rows =
    key === 'involvement'
      ? data.involvement
      : key === 'severity'
        ? data.bySeverity
        : key === 'diagnosis'
          ? data.byDiagnosis
          : key === 'age'
            ? data.byAgeBand
            : data.byFeeTier;
  const tidy = (s: string) => (key === 'fee' ? s.replace(/^\d\s/, '') : key === 'age' ? `${s} yrs` : cap(s));
  const hi = data.involvement.find((i) => i.label === 'high');
  const lo = data.involvement.find((i) => i.label === 'low');
  const c = data.correlations;

  return (
    <Section
      id="drivers"
      eyebrow="Q3 · Drivers"
      title="Parent involvement moves value more than price does"
      lead={
        <>
          High-involvement families get <b>{n2(hi?.value_index ?? 0)}×</b> fair value against{' '}
          <b>{n2(lo?.value_index ?? 0)}×</b> for low. Attendance and improvement rise together (r ={' '}
          <b>{c.attendanceVsImprovement.toFixed(2)}</b>), and the monthly fee barely matters (r ={' '}
          <b>{c.monthlyFeeVsImprovement.toFixed(2)}</b>).
        </>
      }
    >
      <div className="grid-2 even">
        <Card title="Value index by group" sub="Pick a breakdown. The dashed line is fair value.">
          <Seg<Key>
            label="Breakdown"
            value={key}
            onChange={setKey}
            options={(Object.keys(TITLES) as Key[]).map((k) => ({ value: k, label: TITLES[k] }))}
          />
          <BarChart
            ariaLabel={`Value index by ${TITLES[key].toLowerCase()}, dashed line at 1.00`}
            data={rows.map((r) => ({
              label: tidy(r.label),
              value: r.value_index,
              color: r.value_index >= 1 ? 'var(--c-efficient)' : 'var(--c-under)',
              tip: `${tidy(r.label)}: ${n2(r.value_index)}×${r.children ? ` · ${r.children} children` : ''}`,
            }))}
            format={n2}
            refLine={{ value: 1, label: 'fair value' }}
          />
          {key === 'diagnosis' && (
            <p className="count-note">Small groups (for example Cerebral Palsy, 2 children) are unreliable.</p>
          )}
          {key === 'fee' && (
            <p className="count-note">
              Value barely changes with the fee tier, so paying more neither buys nor loses value per rupee.
            </p>
          )}
        </Card>
        <Card title="Attendance against improvement" sub="One dot per child. The dashed blue line is the trend.">
          <Legend
            items={['low', 'medium', 'high'].map((k) => ({
              label: `${cap(k)} involvement`,
              color: INVOLVEMENT_COLOR[k],
            }))}
          />
          <Scatter
            height={330}
            trend
            yFromZero
            points={data.children.map((ch) => ({
              id: ch.code,
              x: ch.attendance,
              y: ch.improvement,
              color: INVOLVEMENT_COLOR[ch.involvement],
              r: 5.5,
              tip: (
                <>
                  <b>{ch.code}</b> · {cap(ch.involvement)} involvement
                  <br />
                  {ch.attendance}% attended · +{ch.improvement} pts
                </>
              ),
            }))}
            xTitle="Attendance (%)"
            yTitle="Improvement (assessment points)"
            xFormat={(v) => `${v}%`}
            ariaLabel="Attendance against improvement for each child, coloured by parent involvement, with a trend line"
          />
        </Card>
      </div>
      <div style={{ marginTop: 20 }}>
        <Card title="By parent involvement">
          <div className="stat-row" style={{ marginTop: 12 }}>
            {data.involvement.map((i) => (
              <Stat
                key={i.label}
                value={`${n2(i.value_index)}×`}
                label={`${cap(i.label)}: ${pct(i.attendance, 0)} attend · +${n1(i.improvement_pts)} pts · ${n1(i.home_tasks_per_week)} home tasks a week`}
              />
            ))}
          </div>
        </Card>
      </div>
    </Section>
  );
}
