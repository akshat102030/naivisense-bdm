import { HBarChart } from '../components/charts/HBarChart';
import { Card, Legend, Section } from '../components/ui';
import { data } from '../data';
import { nice, n1 } from '../lib/format';

const GROUP_COLORS: Record<string, string> = {
  Communication: 'var(--c-thriving)',
  'Motor & Daily Living': 'var(--c-efficient)',
  'Cognition & Learning': 'var(--c-warn)',
  'Behaviour & Regulation': 'var(--c-violet)',
};

export function Domains() {
  const d = data.domains;
  const first = d[0];
  const last = d[d.length - 1];
  return (
    <Section
      id="domains"
      eyebrow="Q4 · Domains"
      title="Which developmental domains improve fastest?"
      alt
      lead={
        <>
          <b>{nice(first.domain)}</b> gains <b>+{n1(first.gain)}</b> points on average and <b>{nice(d[1].domain)}</b>{' '}
          <b>+{n1(d[1].gain)}</b>. The slowest are <b>{nice(last.domain)}</b> (+{n1(last.gain)}) and{' '}
          <b>{nice(d[d.length - 2].domain)}</b> (+
          {n1(d[d.length - 2].gain)}). Gains are measured from each child&apos;s first to latest assessment on a 0–100
          scale.
        </>
      }
    >
      <Card
        title="Average gain by domain"
        sub="Points gained between the initial and the latest assessment, across all children."
      >
        <Legend items={Object.entries(GROUP_COLORS).map(([label, color]) => ({ label, color }))} />
        <HBarChart
          ariaLabel="Average assessment gain in points for each of 15 developmental domains"
          data={d.map((x) => ({
            label: nice(x.domain),
            value: x.gain,
            color: GROUP_COLORS[x.group] ?? 'var(--theme-accent)',
            tip: `${nice(x.domain)} (${x.group}): +${n1(x.gain)} points`,
          }))}
          format={(v) => n1(v)}
        />
      </Card>
    </Section>
  );
}
