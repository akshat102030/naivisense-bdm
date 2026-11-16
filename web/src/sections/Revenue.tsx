import { GroupedBars } from '../components/charts/GroupedBars';
import { Card, Section, Stat } from '../components/ui';
import { data } from '../data';
import { cap, inr, lakh, MONTHS, pct } from '../lib/format';

const STATUS_COLOR: Record<string, string> = {
  paid: 'var(--c-efficient)',
  pending: 'var(--c-warn)',
  failed: 'var(--c-under)',
  refunded: 'var(--c-risk)',
};

export function Revenue({ onSelect }: { onSelect: (code: string) => void }) {
  const k = data.kpi;
  const status = data.revenue.byStatus;
  const total = status.reduce((s, x) => s + x.count, 0);
  const inv = data.involvement;
  return (
    <Section
      id="revenue"
      eyebrow="Q6 · Revenue"
      title="Where does revenue leak?"
      alt
      lead={
        <>
          <b>{inr(k.collected_inr)}</b> collected of <b>{inr(k.billed_inr)}</b> billed (
          <b>{pct(k.collection_rate, 1)}</b>). <b>{inr(k.outstanding_inr)}</b> is outstanding and {k.failed_payments}{' '}
          payments failed. Collection is not worse for low-involvement families ({pct(inv[0].collection_rate)} against{' '}
          {pct(inv[2].collection_rate)} for high), so reminders and retries should reach every family.
        </>
      }
    >
      <div className="grid-2">
        <Card title="Billed and collected by month" sub="Subscription fees, in rupees lakh. November is a part month.">
          <GroupedBars
            ariaLabel="Fees billed and collected by month in rupees lakh"
            rows={data.revenue.monthly.map((m) => ({
              label: MONTHS[Number(m.month.slice(5, 7)) - 1],
              values: { b: m.billed, c: m.collected },
            }))}
            series={[
              { key: 'b', label: 'Billed', color: 'var(--c-series-b)' },
              { key: 'c', label: 'Collected', color: 'var(--theme-accent)' },
            ]}
            format={(v) => (v === 0 ? '0' : lakh(v))}
          />
          <div className="legend" style={{ marginTop: 8 }}>
            <span>
              <i style={{ background: 'var(--c-series-b)' }} />
              Billed
            </span>
            <span>
              <i style={{ background: 'var(--theme-accent)' }} />
              Collected
            </span>
          </div>
        </Card>
        <div className="stack">
          <Card title="Payment status" sub={`${total} subscription and assessment invoices.`}>
            <div className="bar-split" role="img" aria-label={status.map((s) => `${s.status} ${s.count}`).join(', ')}>
              {status.map((s) => (
                <span
                  key={s.status}
                  style={{ width: `${(s.count / total) * 100}%`, background: STATUS_COLOR[s.status] }}
                  title={`${cap(s.status)}: ${s.count}`}
                />
              ))}
            </div>
            <div className="legend" style={{ marginTop: 12 }}>
              {status.map((s) => (
                <span key={s.status}>
                  <i style={{ background: STATUS_COLOR[s.status] }} />
                  {cap(s.status)} {s.count}
                </span>
              ))}
            </div>
          </Card>
          <Card title="Largest balances" sub="Outstanding fees. Select a child for the profile.">
            <ul className="rank">
              {data.revenue.topOutstanding.map((t) => (
                <li key={t.child}>
                  <button type="button" onClick={() => onSelect(t.child)}>
                    <span className="code">{t.child}</span>
                    <span className="meta">outstanding</span>
                    <span className="vi">{inr(t.outstanding_inr)}</span>
                  </button>
                </li>
              ))}
            </ul>
          </Card>
        </div>
      </div>
      <div className="stat-row" style={{ marginTop: 20 }}>
        <Stat value={lakh(k.billed_inr)} label="Billed since May" />
        <Stat value={lakh(k.collected_inr)} label="Collected" />
        <Stat value={lakh(k.outstanding_inr)} label="Outstanding" />
        <Stat value={pct(k.collection_rate, 1)} label="Collection rate" />
      </div>
    </Section>
  );
}
