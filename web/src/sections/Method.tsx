import { Section } from '../components/ui';
import { data } from '../data';

const DOWNLOADS = [
  {
    href: '/downloads/naivisense-bdm-processed-data.zip',
    title: 'Processed data (CSV)',
    note: '13 star-schema tables, child codes only',
  },
  {
    href: '/downloads/Presentation_Script.pdf',
    title: 'Presentation script',
    note: 'Timed 10-minute walk-through (PDF)',
  },
  { href: '/downloads/dashboard.json', title: 'Dashboard data (JSON)', note: 'Everything this page draws' },
];

export function Method() {
  return (
    <Section id="method" eyebrow="Method" title="How the numbers are worked out" alt>
      <div className="grid-2 even">
        <div className="stack">
          <div className="formula">
            <small>Progress Points</small>10 × assessment gain
            <br />+ 20 × session-score gain
            <br />+ 5 × goals completed (floor 0)
          </div>
          <div className="formula">
            <small>Outcome Value Index</small>(child progress ÷ centre progress)
            <br />÷ (child fees ÷ centre fees)
            <br />
            1.00 = fair value
          </div>
        </div>
        <div className="stack">
          <p style={{ margin: 0, lineHeight: 1.6, color: 'var(--theme-text-secondary)' }}>
            Above 1.00 the family received more progress than the fees paid; below 1.00, less. Value groups split
            children at the median fee and median progress: <b>Thriving</b>, <b>Efficient</b>, <b>Under-served</b> and{' '}
            <b>At-risk</b>. Churn risk flags attendance under 70%, or a red clinical band with under 3 points of gain,
            or two or more failed payments.
          </p>
          <p style={{ margin: 0, lineHeight: 1.6, color: 'var(--theme-text-secondary)' }}>
            Therapist value shares each child&apos;s progress and fees by the therapist&apos;s share of attended
            sessions. The centre-wide index is exactly 1.000 by construction.
          </p>
        </div>
      </div>

      <h3 className="display" style={{ margin: '36px 0 14px', fontSize: 24 }}>
        From the app to this page
      </h3>
      <ol className="steps" style={{ padding: 0, margin: 0 }}>
        <li>
          <b>1 · Generate</b>A seeded script writes {data.meta.students} synthetic children, {data.meta.therapists}{' '}
          therapists and their sessions, assessments, alerts and payments into MongoDB with the NaiviSense models.
        </li>
        <li>
          <b>2 · Raw layer</b>13 collections exactly as the app stores them, kept as the audit copy.
        </li>
        <li>
          <b>3 · Processed layer</b>A star schema with dimensions, facts and a child summary. Children are identified by
          code only.
        </li>
        <li>
          <b>4 · Analyse</b>An independent Python script recomputes every number; the same model ships as a Power BI
          project and a written report.
        </li>
      </ol>

      <h3 className="display" style={{ margin: '36px 0 14px', fontSize: 24 }}>
        Limits to keep in mind
      </h3>
      <ul style={{ margin: 0, paddingLeft: 20, lineHeight: 1.7, color: 'var(--theme-text-secondary)' }}>
        <li>
          All data are synthetic. The relationships were designed into the generator, so the findings demonstrate the
          method and do not describe a real centre.
        </li>
        <li>The Progress Points weights (10, 20, 5) are a modelling choice and should be agreed with clinicians.</li>
        <li>
          Therapist attribution is proportional to sessions, not causal. Small groups (for example Cerebral Palsy, 2
          children) are unreliable.
        </li>
        <li>Seven months of data, with November as a part month.</li>
      </ul>

      <h3 className="display" style={{ margin: '36px 0 14px', fontSize: 24 }}>
        Downloads
      </h3>
      <div className="dl-grid">
        {DOWNLOADS.map((d) => (
          <a key={d.href} className="dl" href={d.href} download>
            <b>{d.title}</b>
            <span>{d.note}</span>
          </a>
        ))}
      </div>
    </Section>
  );
}
