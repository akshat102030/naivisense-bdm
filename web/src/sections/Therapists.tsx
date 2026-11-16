import { BarChart } from '../components/charts/BarChart';
import { Card, Section } from '../components/ui';
import { data } from '../data';
import { inr, nice, n1, n2 } from '../lib/format';

const colorFor = (v: number) => (v >= 1 ? 'var(--c-efficient)' : 'var(--c-under)');

export function Therapists() {
  const t = data.therapists;
  const best = t[0];
  const worst = t[t.length - 1];
  return (
    <Section
      id="therapists"
      eyebrow="Q1 · Therapists"
      title="Who delivers the most progress per rupee?"
      lead={
        <>
          <b>{best.name}</b> leads at <b>{n2(best.value_index)}×</b> fair value and <b>{worst.name}</b> trails at{' '}
          <b>{n2(worst.value_index)}×</b>. Therapy types sit close together, so the gap comes from how therapy is
          delivered, not what it costs.
        </>
      }
    >
      <div className="grid-2">
        <Card
          title="Value index by therapist"
          sub="Each child's progress and fees are shared between their therapists by attended-session share. 1.00 is fair value."
        >
          <BarChart
            ariaLabel="Value index by therapist, with a dashed line at 1.00"
            data={t.map((x) => ({
              label: x.name,
              value: x.value_index,
              color: colorFor(x.value_index),
              tip: `${x.name} (${nice(x.specialty)}): ${n2(x.value_index)}× · ${x.sessions.toLocaleString('en-IN')} sessions`,
            }))}
            format={n2}
            refLine={{ value: 1, label: 'fair value 1.00' }}
          />
        </Card>
        <Card title="Value index by therapy type" sub="Fees are similar across types.">
          <BarChart
            height={260}
            ariaLabel="Value index by therapy type"
            data={data.therapyTypes.map((x) => ({
              label: nice(x.label),
              value: x.value_index,
              color: colorFor(x.value_index),
            }))}
            format={n2}
            refLine={{ value: 1, label: '1.00' }}
          />
        </Card>
      </div>
      <div style={{ marginTop: 20 }}>
        <Card title="Therapist scorecard">
          <div className="table-wrap" style={{ marginTop: 12 }}>
            <table className="data">
              <thead>
                <tr>
                  <th>Therapist</th>
                  <th className="l">Specialty</th>
                  <th>Caseload</th>
                  <th>Sessions</th>
                  <th>Fees attributed</th>
                  <th>Progress points</th>
                  <th>Value index</th>
                </tr>
              </thead>
              <tbody>
                {t.map((x) => (
                  <tr key={x.name}>
                    <td>{x.name}</td>
                    <td className="l">{nice(x.specialty)}</td>
                    <td>{x.caseload}</td>
                    <td>{x.sessions.toLocaleString('en-IN')}</td>
                    <td>{inr(x.fees)}</td>
                    <td>{n1(x.progress)}</td>
                    <td style={{ fontWeight: 750, color: colorFor(x.value_index) }}>{n2(x.value_index)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </Section>
  );
}
