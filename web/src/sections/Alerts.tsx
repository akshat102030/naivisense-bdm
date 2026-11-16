import { GroupedBars } from '../components/charts/GroupedBars';
import { HBarChart } from '../components/charts/HBarChart';
import { Card, Section, Stat } from '../components/ui';
import { data } from '../data';
import { cap, n1, pct } from '../lib/format';

export function Alerts() {
  const a = data.alerts;
  const high = a.sla.find((s) => s.severity === 'high');
  const med = a.sla.find((s) => s.severity === 'medium');
  const low = a.sla.find((s) => s.severity === 'low');
  const rows = a.sla.map((s) => ({ label: cap(s.severity), values: { ack: s.avg_hrs_ack, res: s.avg_hrs_resolve } }));
  return (
    <Section
      id="alerts"
      eyebrow="Q5 · Safety alerts"
      title="Severe alerts get answered fast. Routine ones wait."
      lead={
        <>
          High-severity alerts are acknowledged in <b>{n1(high?.avg_hrs_ack ?? 0)} h</b> and every one within 4 hours.
          Medium and low alerts take about <b>{n1(med?.avg_hrs_ack ?? 0)} h</b>, and only{' '}
          {pct(med?.ack_within_4h_pct ?? 0)} are acknowledged within 4 hours. Resolution takes{' '}
          {n1(high?.avg_hrs_resolve ?? 0)} h for high and about {Math.round(low?.avg_hrs_resolve ?? 0)} h for low.
        </>
      }
    >
      <div className="grid-2 even">
        <Card
          title="Hours to acknowledge and to resolve"
          sub="Average from the moment an alert is raised, by severity."
        >
          <GroupedBars
            showValues
            ariaLabel="Average hours to acknowledge and to resolve alerts, by severity"
            rows={rows}
            series={[
              { key: 'ack', label: 'Acknowledge', color: 'var(--theme-accent)' },
              { key: 'res', label: 'Resolve', color: 'var(--c-series-b)' },
            ]}
            format={(v) => (v === 0 ? '0' : v >= 10 ? Math.round(v).toString() : n1(v))}
            yTitle="Hours"
          />
          <div className="legend" style={{ marginTop: 8 }}>
            <span>
              <i style={{ background: 'var(--theme-accent)' }} />
              Acknowledge
            </span>
            <span>
              <i style={{ background: 'var(--c-series-b)' }} />
              Resolve
            </span>
          </div>
        </Card>
        <Card title="Alerts by type" sub={`${a.byType.reduce((s, t) => s + t.count, 0)} alerts in total.`}>
          <HBarChart
            ariaLabel="Number of alerts by type"
            data={a.byType.map((t) => ({ label: cap(t.type), value: t.count, color: 'var(--theme-accent)' }))}
            format={(v) => String(Math.round(v))}
          />
        </Card>
      </div>
      <div style={{ marginTop: 20 }}>
        <div className="stat-row">
          <Stat value={data.kpi.alerts_total} label="Alerts raised" />
          <Stat value={data.kpi.alerts_open} label="Still open (recent)" />
          <Stat value={a.perChildBySeverity.severe} label="Alerts per severe case" />
          <Stat value={a.perChildBySeverity.mild} label="Alerts per mild case" />
        </div>
      </div>
    </Section>
  );
}
