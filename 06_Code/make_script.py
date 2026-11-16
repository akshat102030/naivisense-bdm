"""Builds ../04_Presentation/Presentation_Script.md (+ .html; PDF via headless Chrome). Numbers come from results.json."""
import html, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, 'results.json')))
OUT = os.path.join(HERE, '..', '04_Presentation')
os.makedirs(OUT, exist_ok=True)
inr = lambda v: f'₹{v:,.0f}'
vi = R['vi_by_involvement']; q = R['quadrants']; s = R['alert_sla']; bi = R['by_involvement']
th = sorted(R['vi_by_therapist'].items(), key=lambda kv: -kv[1]['value_index']); dg = list(R['domain_gain'].items()); tier = R['vi_by_monthly_fee_tier']

SEG = [
    ('0', 'Introduction and the one idea', '1:15', 'Home page: title, five KPI cards, six question cards.',
     f'''Good morning, sir. Our project is NaiviSense Therapy Outcome Value Intelligence. A therapy centre bills families every month, but the fee does not say how much a child actually progressed. Our question: which therapy spend earned its price?
We built a synthetic centre of {R["students"]} children and {R["therapists"]} therapists from the NaiviSense MongoDB data model: {R["sessions_past"]:,} sessions, {inr(R["billed_inr"])} of fees, May to November 2026.
The whole dashboard rests on one idea. First, Progress Points: one score for clinical change, session quality and goals: 10 times the assessment gain, 20 times the session-score gain, 5 per goal completed. Then the Outcome Value Index: what share of the centre's progress did this child get, compared with the share of the centre's fees they paid? 1.0 is fair value. Above 1 the family got more than they paid for; below 1, less.
The six cards are our six business questions, and each one is a page.''', None),
    ('1', 'Therapy: therapist and therapy-type efficiency', '1:00', 'The therapist value-index bars (dashed line = 1.0), then the scorecard table.',
     f'''Q1: who gives the most progress per rupee? Fees are similar across therapy types, so differences come from delivery. OT is at {R["vi_by_therapy_type"]["ot"]["value_index"]:.2f} and speech at {R["vi_by_therapy_type"]["speech"]["value_index"]:.2f}; behaviour and special education sit just below 1.
Between therapists the spread is wider: {th[0][0]} leads at {th[0][1]["value_index"]:.2f}, {th[-1][0]} trails at {th[-1][1]["value_index"]:.2f}. We share each child's progress and fees between therapists by their share of attended sessions.''',
     'Coach low-index therapists using the routines of high-index peers.'),
    ('2', 'Value Map', '1:15', 'The scatter. Point to the dashed median lines and the four corners. Hover one dot.',
     f'''Q2: which children are getting value? Every dot is a child. Fees paid run left to right; progress points bottom to top. The dashed lines are the median fee and median progress, which split children into four groups.
Thriving: high fee, high progress, {q["Thriving"]} children. Efficient: low fee, high progress, {q["Efficient"]}. Under-served: high fee, low progress, {q["Under-served"]}. At-risk: low fee, low progress, {q["At-risk"]}.''',
     'Keep Thriving and Efficient plans; review Under-served and re-engage At-risk before they drop out.'),
    ('3', 'At-Risk: who to call', '0:50', 'The three lists: churn-risk, Under-served, Efficient.',
     f'''This page names the children. {R["churn_risk_children"]} are at churn risk: attendance below 70 percent, or a red clinical band with little gain, or two failed payments. {R["red_risk_children"]} are still in the red band, although {R["risk_improved_children"]} children moved to a better band. Right-click any child to drill through to a profile with score history, goals and alerts.''',
     'Call the churn-risk families this week.'),
    ('4', 'Drivers: attendance and parent involvement', '1:15', 'Attendance-vs-improvement scatter with the dashed trend, then value index by involvement.',
     f'''Q3: what drives progress? Attendance and improvement go together, r = {R["corr_attendance_vs_improvement"]:+.2f}. Monthly fee level barely does, r = {R["corr_monthly_fee_vs_improvement"]:+.2f}.
The clearest lever is parent involvement. High-involvement families get {vi["high"]["value_index"]:.2f} times fair value, low-involvement {vi["low"]["value_index"]:.2f}. They attend {bi["high"]["attendance"]:.0%} against {bi["low"]["attendance"]:.0%}, and improve {bi["high"]["improvement_pts"]} points against {bi["low"]["improvement_pts"]}.
By fee tier the index barely moves, {min(v["value_index"] for v in tier.values()):.2f} to {max(v["value_index"] for v in tier.values()):.2f}. Paying more neither buys nor loses value per rupee.''',
     'Spend effort on parent coaching and attendance recovery, not on higher-priced plans.'),
    ('5', 'Domains', '0:45', 'The domain-gain bar chart.',
     f'''Q4: which domains improve fastest? {dg[0][0].replace("_", " ")} gains {dg[0][1]["avg_gain_pts"]} points and {dg[1][0].replace("_", " ")} {dg[1][1]["avg_gain_pts"]}. The slowest are {dg[-1][0].replace("_", " ")} at {dg[-1][1]["avg_gain_pts"]} and {dg[-2][0].replace("_", " ")} at {dg[-2][1]["avg_gain_pts"]}.''',
     'Add targeted therapy blocks for the slowest domains.'),
    ('6', 'Alerts', '0:50', 'Hours-to-acknowledge by severity.',
     f'''Q5: are safety alerts handled in time? Of {R["alerts_total"]} alerts, {R["alerts_open"]} are open. High-severity alerts are acknowledged in {s["high"]["avg_hrs_ack"]} hours and every one within 4 hours. Medium and low alerts wait about {s["medium"]["avg_hrs_ack"]} hours, and only about {s["medium"]["ack_within_4h_pct"]:.0%} are acknowledged within 4 hours.''',
     'Triage works for severe cases; set a same-day target for routine alerts.'),
    ('7', 'Revenue', '0:50', 'Billed vs collected by month, then the outstanding list.',
     f'''Q6: where does revenue leak? We billed {inr(R["billed_inr"])} and collected {inr(R["collected_inr"])}, {R["collection_rate"]:.0%}. {R["failed_payments"]} payments failed and {inr(R["outstanding_inr"])} is outstanding. The gap is not concentrated in low-involvement families: collection is {bi["low"]["collection_rate"]:.0%} for low and {bi["high"]["collection_rate"]:.0%} for high.''',
     'Automate retries and reminders for every family.'),
    ('8', 'Methodology, data and architecture', '0:50', 'Methodology page, then the architecture figure or Model view.',
     '''The data come from the NaiviSense MongoDB model. We generate 50 synthetic children with a fixed seed and store them twice: a raw layer exactly as the app saves it, and a processed star schema with dimensions and facts. Power BI reads the processed layer; all 53 measures are written in DAX.
Data flow in one line: app collections, raw layer, processing script, processed layer in MongoDB and CSV, Power BI model, dashboard.
Our own check: a separate Python script recomputes every number from the processed files, and the centre value index is exactly 1.0.''', None),
    ('9', 'Conclusion', '0:40', 'Back to Home.',
     '''Three lessons for a therapy centre. One: parent involvement and attendance move value more than price does. Two: severe cases and routine alerts are where the centre under-serves today. Three: judge plans by progress per rupee, not by fee. Thank you, sir. We are happy to take questions.''', None),
]
QA = [
    ('Why not just use the assessment score?', 'Scores, session quality and goals measure different things. Progress Points combine them on one scale so children with different baselines can be compared.'),
    ('Why compare with the centre\'s own totals?', 'Shares of centre progress and centre fees remove the effect of the overall scale, so the index is a fair relative measure and averages exactly 1.0.'),
    ('Is this real data?', 'No. It is synthetic, generated from the app\'s data model with designed relationships, so the findings demonstrate the method. The same pipeline can run on real collections.'),
    ('Why are the weights 10, 20 and 5?', 'They are a modelling choice that balances clinical change, session quality and goals; they should be agreed with clinicians, and the index is easy to recompute with different weights.'),
    ('Why MongoDB, and why two layers?', 'The app already stores data in MongoDB. The raw layer is the audit copy; the processed layer is flat and analysis-ready, which Power BI needs.'),
    ('Limitations?', 'Synthetic data, seven months, therapist attribution proportional to sessions rather than causal, and small subgroups such as Cerebral Palsy (2 children).'),
    ('Did you check the DAX in Power BI?', 'The numbers are verified by an independent Python script; the QA page in the report carries the expected values for the final check in Desktop.'),
]

md = ['# NaiviSense Therapy Outcome Value: Presentation Script', '', f'Target length about 10 minutes. {R["students"]} children · {R["therapists"]} therapists · May–Nov 2026 · synthetic data.', '']
for n, title, t, show, say, sowhat in SEG:
    md += [f'## {n} {title} · {t}', f'**SHOW:** {show}', '', *say.split('\n'), '']
    if sowhat: md += [f'**So what:** {sowhat}', '']
md += ['## Likely questions: short answers', '']
for a, b in QA: md += [f'**{a}** {b}', '']
open(os.path.join(OUT, 'Presentation_Script.md'), 'w').write('\n'.join(md))


def inline(t): return re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', html.escape(t))


body = ''
for line in md:
    if line.startswith('# '): body += f'<h1>{inline(line[2:])}</h1>'
    elif line.startswith('## '): body += f'<h2>{inline(line[3:])}</h2>'
    elif line.startswith('**SHOW:**'): body += f'<p class="show">{inline(line)}</p>'
    elif line.startswith('**So what:**'): body += f'<p class="sw">{inline(line)}</p>'
    elif line.strip(): body += f'<p>{inline(line)}</p>'
open(os.path.join(OUT, 'Presentation_Script.html'), 'w').write(
    '<!doctype html><meta charset="utf-8"><style>@page{size:A4;margin:16mm}body{font:11pt/1.45 Georgia,serif;color:#1F1D1A}h1{font:700 20pt Helvetica,Arial;margin:0 0 4px}'
    'h2{font:700 12.5pt Helvetica,Arial;margin:16px 0 4px;color:#2F8F83;break-after:avoid}p{margin:5px 0}.show{background:#F6F4EF;padding:5px 8px;border-left:3px solid #2F8F83;font:9.5pt Helvetica,Arial}'
    '.sw{font-weight:700}</style>' + body)
print('script written')
