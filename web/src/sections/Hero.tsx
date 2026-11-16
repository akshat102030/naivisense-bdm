import { data, GROUPS, GROUP_COLOR, GROUP_HINT } from '../data';
import { n1, n2, pct } from '../lib/format';

export function Hero() {
  const k = data.kpi;
  const hi = data.involvement.find((i) => i.label === 'high');
  const lo = data.involvement.find((i) => i.label === 'low');
  return (
    <section className="hero" aria-labelledby="hero-title">
      <div className="wrap">
        <div className="hero-grid">
          <div>
            <span className="eyebrow">
              <span className="dot" />
              BDM project · {data.meta.period} · synthetic data
            </span>
            <h1 id="hero-title">
              Which therapy rupees <em>moved a child forward?</em>
            </h1>
            <p className="lead">
              A therapy fee says little about how much a child progressed. We scored {k.students} children on one{' '}
              <b>Progress Points</b> scale and compared each child&apos;s share of progress with their share of fees.
              High-involvement families get <b>{n2(hi?.value_index ?? 0)}×</b> fair value; low-involvement families get{' '}
              <b>{n2(lo?.value_index ?? 0)}×</b>.
            </p>
            <div className="cta-row">
              <a className="btn primary" href="#value-map">
                Open the value map
              </a>
              <a className="btn" href="#explorer">
                Explore the children
              </a>
              <a className="btn" href="#method">
                How it is measured
              </a>
            </div>
          </div>
          <aside className="glance" aria-label="Children by value group">
            <h2>The centre at a glance</h2>
            <p>Every child falls in one of four value groups.</p>
            <div className="tiles">
              {GROUPS.map((g) => (
                <div className="tile" key={g}>
                  <div className="n" style={{ color: GROUP_COLOR[g] }}>
                    {data.quadrants[g]}
                  </div>
                  <div className="t">{g}</div>
                  <div className="h">{GROUP_HINT[g]}</div>
                </div>
              ))}
            </div>
          </aside>
        </div>
        <div className="kpis">
          <div className="kpi">
            <div className="v">{k.students}</div>
            <div className="l">Children</div>
            <div className="s">{k.therapists} therapists</div>
          </div>
          <div className="kpi">
            <div className="v">{pct(k.attendance_rate, 1)}</div>
            <div className="l">Sessions attended</div>
            <div className="s">
              {k.sessions_attended.toLocaleString('en-IN')} of {k.sessions_past.toLocaleString('en-IN')}
            </div>
          </div>
          <div className="kpi">
            <div className="v">+{n1(k.avg_improvement_pts)}</div>
            <div className="l">Avg improvement</div>
            <div className="s">assessment points</div>
          </div>
          <div className="kpi">
            <div className="v">{pct(k.collection_rate, 1)}</div>
            <div className="l">Fees collected</div>
            <div className="s">{k.failed_payments} failed payments</div>
          </div>
          <div className="kpi">
            <div className="v">{k.churn_risk_children}</div>
            <div className="l">At churn risk</div>
            <div className="s">{k.red_risk_children} still in red band</div>
          </div>
        </div>
      </div>
    </section>
  );
}
