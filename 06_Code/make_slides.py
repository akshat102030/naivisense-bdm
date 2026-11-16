"""Builds ../04_Presentation/NaiviSense_Outcome_Value_Slides.pdf (16:9 deck) from results.json and the report figures.

    python3 make_slides.py        # writes the .html; then prints the PDF with headless Chrome (path below)
"""
import html, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, 'results.json')))
OUTDIR = os.path.abspath(os.path.join(HERE, '..', '04_Presentation'))
FIG = os.path.abspath(os.path.join(HERE, '..', '03_Report', 'figures'))
FONTS = os.path.abspath(os.path.join(HERE, '..', 'web', 'public', 'fonts'))
HTML = os.path.join(OUTDIR, '_slides.html')
PDF = os.path.join(OUTDIR, 'NaiviSense_Outcome_Value_Slides.pdf')
CHROME = os.environ.get('CHROME', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
LIVE = 'https://naivisense-bdm.netlify.app'
REPO = 'github.com/akshat102030/naivisense-bdm'

inr = lambda v: f'₹{v:,.0f}'
lakh = lambda v: f'₹{v / 1e5:.1f} L'
vi = R['vi_by_involvement']; bi = R['by_involvement']; q = R['quadrants']; s = R['alert_sla']
th = sorted(R['vi_by_therapist'].items(), key=lambda kv: -kv[1]['value_index'])
dg = list(R['domain_gain'].items()); tier = R['vi_by_monthly_fee_tier']; sv = R['vi_by_severity']
nice = lambda k: k.replace('_', ' ')

slides = []


def slide(title, body, kicker='', num=True):
    slides.append((kicker, title, body, num))


def fig(name, cap=''):
    return f'<figure><img src="file://{FIG}/{name}" alt="{html.escape(cap)}"></figure>'


def side(points, big=None):
    out = '<div class="side">'
    if big:
        out += f'<div class="big"><b>{big[0]}</b><span>{big[1]}</span></div>'
    out += ''.join(f'<p>{p}</p>' for p in points) + '</div>'
    return out


slide('', f'''<div class="title">
  <span class="eyebrow">BDM project · Semester VII · synthetic data</span>
  <h1>Which therapy rupees <em>moved a child forward?</em></h1>
  <p class="lead">Scoring {R["students"]} children on one Progress Points scale, and comparing each child's share of progress with their share of fees.</p>
  <p class="meta">NaiviSense Outcome Value Intelligence · {R["therapists"]} therapists · May–Nov 2026</p>
</div>''', num=False)

slide('One idea: progress per rupee', f'''<div class="two">
  <div>
    <div class="formula"><small>Progress Points</small>10 × assessment gain<br>+ 20 × session-score gain<br>+ 5 × goals completed</div>
    <div class="formula"><small>Outcome Value Index</small>(child progress ÷ centre progress)<br>÷ (child fees ÷ centre fees)<br>1.00 = fair value</div>
  </div>
  <div class="groups">
    <div class="g" style="--c:#2c6fbf"><b>{q["Thriving"]}</b><span>Thriving</span><i>high fees, high progress</i></div>
    <div class="g" style="--c:#2a9d68"><b>{q["Efficient"]}</b><span>Efficient</span><i>lower fees, high progress</i></div>
    <div class="g" style="--c:#d4524c"><b>{q["Under-served"]}</b><span>Under-served</span><i>high fees, low progress</i></div>
    <div class="g" style="--c:#8a93a3"><b>{q["At-risk"]}</b><span>At-risk</span><i>lower fees, low progress</i></div>
  </div>
</div>''', 'Method')

slide('From the app to the dashboard', f'''<div class="steps">
  <div><b>1 · Generate</b>A seeded script writes {R["students"]} synthetic children, their sessions, assessments, alerts and payments into MongoDB, using the NaiviSense models.</div>
  <div><b>2 · Raw layer</b>13 collections exactly as the app stores them. The audit copy.</div>
  <div><b>3 · Processed layer</b>A star schema: dimensions, facts and a child summary. Children appear by code only.</div>
  <div><b>4 · Analyse</b>An independent Python script recomputes every number. Same model in Power BI, a report and a web dashboard.</div>
</div>
<div class="nums"><div><b>{R["students"]}</b>children</div><div><b>{R["sessions_past"]:,}</b>sessions</div><div><b>{lakh(R["billed_inr"])}</b>billed</div><div><b>{R["alerts_total"]}</b>alerts</div><div><b>6</b>months</div></div>''', 'Data')

slide(f'{th[0][0]} leads at {th[0][1]["value_index"]:.2f}×; {th[-1][0]} trails at {th[-1][1]["value_index"]:.2f}×',
      '<div class="split">' + fig('fig_therapist.png', 'Value index by therapist') + side([
          f'Therapy types sit close together (OT {R["vi_by_therapy_type"]["ot"]["value_index"]:.2f}, speech {R["vi_by_therapy_type"]["speech"]["value_index"]:.2f}, behaviour {R["vi_by_therapy_type"]["behavior"]["value_index"]:.2f}, special education {R["vi_by_therapy_type"]["special_ed"]["value_index"]:.2f}).',
          '<b>So what:</b> the gap comes from how therapy is delivered, not what it costs. Pair low-index therapists with high-index peers.']) + '</div>', 'Q1 · Therapists')

slide(f'{q["Thriving"]} Thriving, {q["Efficient"]} Efficient, {q["Under-served"]} Under-served, {q["At-risk"]} At-risk',
      '<div class="split">' + fig('fig_valuemap.png', 'Value map') + side([
          f'Under-served children pay above-median fees ({inr(R["median_fee"])}) for below-median progress.',
          f'{R["churn_risk_children"]} children are at churn risk; {R["red_risk_children"]} are still in the red clinical band, though {R["risk_improved_children"]} moved to a better band.',
          '<b>So what:</b> review the Under-served plans first; re-engage At-risk families before they drop out.']) + '</div>', 'Q2 · Value map')

slide(f'Parent involvement moves value more than price: {vi["high"]["value_index"]:.2f}× vs {vi["low"]["value_index"]:.2f}×',
      '<div class="split wide">' + fig('fig_drivers.png', 'Drivers') + side([
          f'Attendance vs improvement r = <b>{R["corr_attendance_vs_improvement"]:+.2f}</b>; monthly fee vs improvement r = <b>{R["corr_monthly_fee_vs_improvement"]:+.2f}</b>.',
          f'High involvement: {bi["high"]["attendance"]:.0%} attend, +{bi["high"]["improvement_pts"]} pts. Low: {bi["low"]["attendance"]:.0%}, +{bi["low"]["improvement_pts"]}.',
          f'By fee tier the index barely moves ({min(v["value_index"] for v in tier.values()):.2f}–{max(v["value_index"] for v in tier.values()):.2f}).',
          '<b>So what:</b> invest in parent coaching and attendance recovery, not higher-priced plans.']) + '</div>', 'Q3 · Drivers')

slide(f'{nice(dg[0][0]).capitalize()} and {nice(dg[1][0])} improve fastest',
      '<div class="split">' + fig('fig_domains.png', 'Domains') + side([
          f'Gains run from +{dg[0][1]["avg_gain_pts"]} ({nice(dg[0][0])}) down to +{dg[-1][1]["avg_gain_pts"]} ({nice(dg[-1][0])}) on a 0–100 scale.',
          f'Severe cases return {sv["severe"]["value_index"]:.2f}× fair value against {sv["moderate"]["value_index"]:.2f}× for moderate, so a flat fee under-serves the hardest cases.',
          '<b>So what:</b> add targeted therapy blocks for the slowest domains; review pricing for severe cases.']) + '</div>', 'Q4 · Domains')

slide('Severe alerts get answered fast. Routine ones wait.',
      '<div class="split wide">' + fig('fig_alerts.png', 'Alerts') + side([
          f'High severity: acknowledged in <b>{s["high"]["avg_hrs_ack"]} h</b>, resolved in {s["high"]["avg_hrs_resolve"]} h; every one within 4 hours.',
          f'Medium and low: about <b>{s["medium"]["avg_hrs_ack"]} h</b> to acknowledge; only {s["medium"]["ack_within_4h_pct"]:.0%} within 4 hours.',
          '<b>So what:</b> set a same-day acknowledgement target for medium and low alerts.']) + '</div>', 'Q5 · Alerts')

slide(f'{lakh(R["collected_inr"])} collected of {lakh(R["billed_inr"])} billed ({R["collection_rate"]:.1%})',
      '<div class="split">' + fig('fig_revenue.png', 'Revenue') + side([
          f'{R["failed_payments"]} payments failed; {inr(R["outstanding_inr"])} is outstanding.',
          f'Collection is not worse for low-involvement families ({bi["low"]["collection_rate"]:.0%} vs {bi["high"]["collection_rate"]:.0%} for high).',
          '<b>So what:</b> automate retries and reminders for every family.']) + '</div>', 'Q6 · Revenue')

slide('Recommendations', '''<ul class="recs">
  <li><b>Coach parents</b> and recover attendance before raising fees: involvement and attendance move value, fee tier does not.</li>
  <li><b>Review the Under-served list</b> and call churn-risk families first.</li>
  <li><b>Pair therapists:</b> low-index with high-index peers, and compare session routines.</li>
  <li><b>Speed up routine alerts:</b> same-day acknowledgement for medium and low.</li>
  <li><b>Re-price severe cases:</b> they return the least progress per rupee on a flat fee.</li>
  <li><b>Automate payment retries</b> and reminders for all families.</li>
</ul>''', 'Action')

slide('Limits, and where to find everything', f'''<div class="two">
  <ul class="recs small">
    <li>All data are synthetic and the relationships were designed in, so findings demonstrate the method, not a real centre.</li>
    <li>Progress Points weights (10, 20, 5) are a modelling choice to agree with clinicians.</li>
    <li>Therapist attribution is by session share, not causal. Small groups are unreliable.</li>
    <li>Seven months of data; November is a part month.</li>
  </ul>
  <div class="links">
    <div><b>Live dashboard</b>{LIVE.replace("https://", "")}</div>
    <div><b>Source and data</b>{REPO}</div>
    <div><b>Also in the repo</b>Power BI project · written report · generator</div>
  </div>
</div>
<p class="thanks">Thank you. Questions?</p>''', 'Close')

pages = ''
total = len(slides)
for i, (kicker, title, body, num) in enumerate(slides, 1):
    head = '' if not title else f'<header>{f"<span class=eyebrow>{kicker}</span>" if kicker else ""}<h2>{title}</h2></header>'
    foot = f'<footer><span>NaiviSense Outcome Value · BDM project · synthetic data</span><span>{i} / {total}</span></footer>' if num else ''
    pages += f'<section class="slide{" cover" if not title else ""}">{head}<div class="body">{body}</div>{foot}</section>\n'

css = f'''
@font-face{{font-family:'Inter';font-weight:100 900;src:url('file://{FONTS}/inter-latin-wght-v5.3.0.woff2') format('woff2-variations')}}
@font-face{{font-family:'Bricolage Grotesque';font-weight:200 800;src:url('file://{FONTS}/bricolage-grotesque-latin-opsz-v5.3.0.woff2') format('woff2-variations')}}
@page{{size:1280px 720px;margin:0}}
*{{box-sizing:border-box}} html,body{{margin:0;font-family:Inter,sans-serif;color:#111827;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.slide{{width:1280px;height:720px;padding:48px 64px 40px;background:#FAF8F4;position:relative;overflow:hidden;page-break-after:always;display:flex;flex-direction:column}}
header{{margin-bottom:22px}} .eyebrow{{display:block;font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#2c6fbf;margin-bottom:8px}}
h2{{margin:0;font:800 38px/1.08 'Bricolage Grotesque',sans-serif;letter-spacing:-.02em;max-width:1050px}}
.body{{flex:1;min-height:0}} footer{{position:absolute;left:64px;right:64px;bottom:22px;display:flex;justify-content:space-between;font-size:12px;color:#6b7280}}
.cover{{background:#FAF8F4}} .title{{height:100%;display:flex;flex-direction:column;justify-content:center;gap:18px}}
.title h1{{margin:0;font:800 76px/1 'Bricolage Grotesque',sans-serif;letter-spacing:-.03em;max-width:900px}} .title em{{font-style:normal;color:#2c6fbf}}
.lead{{font-size:22px;line-height:1.5;color:#4b5563;max-width:780px;margin:0}} .meta{{font-size:15px;color:#6b7280;margin:0}}
.split{{display:grid;grid-template-columns:1.25fr 1fr;gap:36px;height:100%;align-items:center}} .split.wide{{grid-template-columns:1.6fr 1fr}}
figure{{margin:0;background:#fff;border:1px solid rgba(15,23,42,.08);border-radius:20px;padding:14px}}
figure img{{width:100%;display:block;max-height:470px;object-fit:contain}}
.side p{{font-size:18px;line-height:1.5;color:#374151;margin:0 0 16px}} .side p b{{color:#111827}}
.two{{display:grid;grid-template-columns:1.1fr 1fr;gap:36px;align-items:start}}
.formula{{background:#0a1428;color:#e8eefb;border-radius:18px;padding:20px 24px;font:600 18px/1.7 ui-monospace,Menlo,monospace;margin-bottom:18px}}
.formula small{{display:block;font:700 12px Inter,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:#8fb4e8;margin-bottom:6px}}
.groups{{display:grid;grid-template-columns:1fr 1fr;gap:14px}} .g{{background:#fff;border:1px solid rgba(15,23,42,.08);border-radius:18px;padding:20px}}
.g b{{display:block;font:800 52px/1 'Bricolage Grotesque',sans-serif;color:var(--c)}} .g span{{display:block;font-weight:700;font-size:18px;margin-top:8px}} .g i{{font-style:normal;font-size:14px;color:#6b7280}}
.steps{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}} .steps div{{background:#fff;border:1px solid rgba(15,23,42,.08);border-radius:18px;padding:20px;font-size:16px;line-height:1.5;color:#4b5563}}
.steps b{{display:block;font:700 19px 'Bricolage Grotesque',sans-serif;color:#111827;margin-bottom:8px}}
.nums{{display:flex;gap:16px;margin-top:28px}} .nums div{{flex:1;background:#E3EEFB;border-radius:18px;padding:20px;font-size:15px;color:#1b4676}} .nums b{{display:block;font:800 36px 'Bricolage Grotesque',sans-serif;color:#2c6fbf}}
.recs{{list-style:none;margin:0;padding:0;display:grid;gap:14px}} .recs li{{background:#fff;border:1px solid rgba(15,23,42,.08);border-radius:16px;padding:16px 22px;font-size:20px;line-height:1.4;color:#374151}} .recs b{{color:#111827}}
.recs.small li{{font-size:17px;padding:14px 18px}} .links{{display:grid;gap:14px}} .links div{{background:#0a1428;color:#e8eefb;border-radius:16px;padding:18px 22px;font-size:18px}} .links b{{display:block;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:#8fb4e8;margin-bottom:4px}}
.thanks{{font:800 34px 'Bricolage Grotesque',sans-serif;margin:26px 0 0;color:#2c6fbf}}
'''
open(HTML, 'w').write(f'<!doctype html><meta charset="utf-8"><title>NaiviSense Outcome Value</title><style>{css}</style>{pages}')
r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-pdf-header-footer', f'--print-to-pdf={PDF}', f'file://{HTML}'], capture_output=True, text=True)
os.remove(HTML)
print('slides:', total, '->', PDF, os.path.getsize(PDF), 'bytes')
sys.exit(0 if os.path.exists(PDF) else 1)
