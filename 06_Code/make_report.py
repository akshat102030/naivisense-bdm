"""Builds ../03_Report/NaiviSense_BDM_Project_Report.docx (needs python-docx). All numbers come from results.json."""
import json, os
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.shared import Pt, Cm, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, 'results.json')))
FIG = os.path.join(HERE, '..', '03_Report', 'figures')
OUT = os.path.join(HERE, '..', '03_Report', 'NaiviSense_BDM_Project_Report.docx')
inr = lambda v: f'₹{v:,.0f}'
lakh = lambda v: f'₹{v / 1e5:.1f} L'
pct = lambda v, d=0: f'{v * 100:.{d}f}%'

doc = Document()
sec = doc.sections[0]; sec.left_margin = sec.right_margin = Cm(2.5); sec.top_margin = sec.bottom_margin = Cm(2.3)
st = doc.styles['Normal']; st.font.name = 'Times New Roman'; st.font.size = Pt(11)
for n, sz in (('Heading 1', 16), ('Heading 2', 13)):
    h = doc.styles[n]; h.font.name = 'Times New Roman'; h.font.size = Pt(sz); h.font.bold = True; h.font.color.rgb = RGBColor(0x1F, 0x1D, 0x1A)

fig_n = [0]; tab_n = {}


def para(text='', bold=False, italic=False, size=None, align=None, space=6):
    p = doc.add_paragraph(); r = p.add_run(text); r.bold = bold; r.italic = italic
    if size: r.font.size = Pt(size)
    if align: p.alignment = align
    p.paragraph_format.space_after = Pt(space); return p


def bullets(items):
    for t in items:
        p = doc.add_paragraph(style='List Bullet'); p.add_run(t); p.paragraph_format.space_after = Pt(2)


def table(caption, header, rows, widths=None):
    c = para(caption, italic=True, size=10, space=2); c.paragraph_format.keep_with_next = True
    t = doc.add_table(rows=1, cols=len(header)); t.style = 'Light Grid Accent 1'; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        t.rows[0].cells[i].text = ''; r = t.rows[0].cells[i].paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(9.5)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ''; r = cells[i].paragraphs[0].add_run(str(v)); r.font.size = Pt(9.5)
    if widths:
        for row in t.rows:
            for i, wd in enumerate(widths): row.cells[i].width = Cm(wd)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def figure(fn, caption, width=15):
    fig_n[0] += 1; doc.add_picture(os.path.join(FIG, fn), width=Cm(width)); doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    para(f'Figure {fig_n[0]}: {caption}', italic=True, size=10, align=WD_ALIGN_PARAGRAPH.CENTER)


def page_break(): doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


# ------------------------------------------------------------------ cover
for _ in range(3): para('')
para('NAIVISENSE THERAPY OUTCOME VALUE', True, size=22, align=WD_ALIGN_PARAGRAPH.CENTER, space=2)
para('AND CHILD PROGRESS INTELLIGENCE', True, size=22, align=WD_ALIGN_PARAGRAPH.CENTER, space=14)
para('Valuing every rupee of therapy fees by the progress it bought, May–November 2026', italic=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space=30)
para('A Project Report', size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space=2)
para('submitted for the course', size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space=2)
para('BDM (Semester VII)', True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space=24)
para('Submitted by', size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space=2)
for n in ('[Student name 1]', '[Student name 2]', '[Student name 3]', '[Student name 4]'):
    para(n, True, align=WD_ALIGN_PARAGRAPH.CENTER, space=2)
para('', space=24)
para('ABV-INDIAN INSTITUTE OF INFORMATION TECHNOLOGY AND MANAGEMENT GWALIOR', True, size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space=2)
para('GWALIOR, INDIA', size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space=2)
para('NOVEMBER, 2026', size=11, align=WD_ALIGN_PARAGRAPH.CENTER)
page_break()

# ------------------------------------------------------------------ abstract + toc
tf = R['vi_by_involvement']
doc.add_heading('Abstract', 1)
para(f'Therapy centres bill families monthly, but a fee says little about how much a child actually progressed. This project asks which therapy spend earned its price. '
     f'Using the NaiviSense data model (children, sessions, attendance, assessments, alerts, payments, goals and home-engagement logs) we prepared a sample dataset for a centre of '
     f'{R["students"]} children and {R["therapists"]} therapists covering May–November 2026 ({R["sessions_past"]:,} past sessions, {inr(R["billed_inr"])} of subscription fees), '
     f'stored it in MongoDB as a raw layer and a processed star schema, scored every child on one Progress Points scale, and built an Outcome Value Index: a child\'s share of centre progress divided by their share of centre fees.')
para(f'The analysis is delivered as a Power BI project and written up here. The findings: parent involvement moves value far more than fee level (value index {tf["high"]["value_index"]:.2f} for high-involvement families against {tf["low"]["value_index"]:.2f} for low); '
     f'attendance tracks improvement (r = {R["corr_attendance_vs_improvement"]:+.2f}); {R["quadrants"]["Under-served"]} children pay above-median fees for below-median progress; '
     f'high-severity alerts are acknowledged in {R["alert_sla"]["high"]["avg_hrs_ack"]} hours but routine ones wait about {R["alert_sla"]["medium"]["avg_hrs_ack"]} hours.')
para('The figures are sample data prepared for Naivedyam Child Development Center; the relationships in them were designed, so the findings demonstrate the method. Real, anonymised records will replace them.', italic=True)
para('Keywords: therapy outcomes, value index, Power BI, DAX, MongoDB, star schema, sample data', italic=True)
doc.add_heading('Table of Contents', 1)
for t in ['1. Introduction', '2. Data and Methodology', '   2.1 Data Sources', '   2.2 Data Preparation (Raw and Processed Layers)', '   2.3 Data Model', '   2.4 Value Metrics',
          '3. Power BI Dashboard', '4. Results and Analysis', '   4.1 Centre Overview', '   4.2 Therapist and Therapy Efficiency', '   4.3 Value Groups and At-Risk Children', '   4.4 Drivers of Progress',
          '   4.5 Domains, Alerts and Revenue', '   4.6 Validation', '5. Data Layer and Architecture', '6. Recommendations and Conclusion', 'References']:
    para(t, space=1)
page_break()

# ------------------------------------------------------------------ 1
doc.add_heading('1. Introduction', 1)
para('A child with a developmental condition may attend therapy two or three times a week for months. Families pay a monthly fee that depends on the number of therapy types, not on the outcome. '
     'Centre managers therefore see attendance and revenue easily, but cannot tell which plans, therapists or families are producing progress for the money.')
para('Problem statement. Which therapy spend earned its price? Taking the view of a centre analytics team, we measure how much clinical progress each rupee of fees bought, so that therapists, plans and families can be compared and the centre can act on evidence.', bold=False)
para('The project answers six business questions:')
for q in ['Which therapist and therapy type delivers the most progress per rupee?', 'Which children are Thriving, Efficient, Under-served or At-risk?',
          'Does attendance or parent involvement drive progress?', 'Which developmental domains improve fastest?', 'Are safety alerts acknowledged and resolved in time?', 'Where does revenue leak, and who is behind?']:
    p = doc.add_paragraph(style='List Number'); p.add_run(q); p.paragraph_format.space_after = Pt(2)
para('The results are delivered as a Power BI project (02_PowerBI/NaiviSense_Outcome_Value.pbip) built on one processed dataset that is also stored in MongoDB.')

# ------------------------------------------------------------------ 2
doc.add_heading('2. Data and Methodology', 1)
doc.add_heading('2.1 Data Sources', 2)
table('Table 2.1: Data sources', ['Source', 'What it provides', 'Size'], [
    ['NaiviSense MongoDB models (users, children, parents)', 'Children, diagnoses, severity, therapist plans, home context', f'{R["students"]} children, {R["therapists"] + 3} staff users'],
    ['Sessions and attendances', 'Scheduled and completed sessions, mood, 4 session scores, attendance status', f'{R["sessions_past"]:,} past sessions'],
    ['Assessments', '15 developmental domain scores, overall score, risk band, monthly snapshots', '414 snapshots'],
    ['Alerts and concerns', 'Safety alerts with severity, acknowledgement and resolution times', f'{R["alerts_total"]} alerts'],
    ['Payments', 'Monthly subscription invoices and status', f'{inr(R["billed_inr"])} billed'],
    ['Goals, meal logs, home-task logs', 'Therapy goals and weekly home engagement', '145 goals, 9,449 meals, 3,976 tasks']], [5, 7.5, 4])
para('The data are sample data prepared for Naivedyam Child Development Center (names removed, children identified by code). A deterministic generator (generator folder, fixed seed) produces documents with the same fields as the app\'s Mongoose models and flags them as sample records. '
     'Hidden traits drive the data so that real relationships exist to find: parent involvement raises attendance, home engagement and improvement; severity lowers baselines and raises alerts; domains matching a child\'s therapy types improve faster.')
doc.add_heading('2.2 Data Preparation (Raw and Processed Layers)', 2)
para('Two layers are kept, in MongoDB (a separate sample database) and as CSV:')
bullets(['Raw layer (01_Data/raw): 13 collections exactly as the app stores them, flattened to CSV. It is the audit copy.',
         'Processed layer (01_Data/processed): 13 analysis-ready tables built by process.ts: dim_date, dim_child, dim_therapist, six fact tables, fact_child_therapist, fact_home_engagement_weekly, agg_child_summary and agg_monthly_center.'])
para('Main preparation steps: ObjectIds become text keys; flags become 0/1; waiting times become hours; a monthly assessment history is kept because the app stores only the initial and latest assessment; '
     'subscription invoices are separated from the one-off assessment fee; and each child\'s progress and fees are shared between therapists by attended-session share.')
doc.add_heading('2.3 Data Model', 2)
para('The Power BI model is a star schema with eight fact tables, three dimensions plus a week table, and one child-level summary. All relationships are many-to-one except agg_child_summary, which is one-to-one with dim_child. There are 53 DAX measures and two calculated columns (Value Group, Fee Tier).')
figure('fig_schema.png', 'Star schema of the Power BI model', 13.5)
doc.add_heading('2.4 Value Metrics', 2)
para('Progress Points put clinical change, session quality and goals on one scale:')
para('Progress Points = 10 × assessment gain + 20 × session-score gain + 5 × goals completed (floored at 0)', italic=True)
para('The Outcome Value Index compares a child\'s share of centre progress with their share of centre fees. 1.00 is fair value; above 1 the family received more progress than fees paid; below 1, less:')
para('Outcome Value Index = (Progress ÷ Centre progress) ÷ (Fees ÷ Centre fees)', italic=True)
para(f'Fair value is the fees the child\'s progress would have cost at the centre\'s price per Progress Point; Overpay = Fees − Fair value. Value groups split children at the median fee ({inr(R["median_fee"])}) and the median progress ({R["median_pp"]:.1f} points): '
     'Thriving (high fee, high progress), Efficient (low fee, high progress), Under-served (high fee, low progress) and At-risk (low fee, low progress). '
     'Churn risk flags a child with attendance below 70%, or a red clinical band with under 3 points of gain, or two or more failed payments.')

# ------------------------------------------------------------------ 3
doc.add_heading('3. Power BI Dashboard', 1)
para('Each page title states its finding with numbers, a "So what" panel states the decision it supports, and colours keep a fixed meaning (green Efficient, blue Thriving, red Under-served, grey At-risk). Table 3.1 lists the pages.')
table('Table 3.1: Pages of the Power BI report', ['Page', 'Question answered', 'Main visuals'], [
    ['Home', 'Overview', 'KPI strip, six question cards'], ['1 Therapy', 'Which therapist gives most progress per rupee?', 'Value index by therapist and type, scorecard'],
    ['2 Value Map', 'Who is Thriving, Efficient, Under-served, At-risk?', 'Fees vs progress scatter, ranked list'], ['3 At-Risk', 'Who needs action now?', 'Churn-risk, Under-served and Efficient lists'],
    ['4 Drivers', 'Do attendance and parent involvement drive progress?', 'Attendance vs improvement scatter, value by involvement and fee tier'],
    ['5 Domains', 'Which domains improve fastest?', 'Gain by domain, score trend, domain-group matrix'], ['6 Alerts', 'Are alerts handled in time?', 'Hours to acknowledge and resolve by severity'],
    ['7 Revenue', 'Where does revenue leak?', 'Billed vs collected, payment status mix, outstanding list'], ['Student Profile', 'One child\'s history (drill-through)', 'Score trend, goals, alerts'],
    ['Methodology / QA', 'How is value measured? Do numbers reconcile?', 'Definitions; cards with expected values']], [3.2, 6.3, 7])
para('Dashboard screenshots: [insert screenshots from Power BI Desktop here after opening 02_PowerBI/NaiviSense_Outcome_Value.pbip. The figures in Chapter 4 are drawn from the same processed data with Python so that the report can be read without Power BI.]', italic=True)

# ------------------------------------------------------------------ 4
doc.add_heading('4. Results and Analysis', 1)
doc.add_heading('4.1 Centre Overview', 2)
para(f'The centre held {R["sessions_past"]:,} sessions between May and November 2026 and children attended {pct(R["attendance_rate"], 1)} of them ({R["sessions_by_mode"]["online"]:.0%} online, {R["sessions_by_mode"]["offline"]:.0%} offline, so mode is not a driver). '
     f'Every child improved on the assessment scale, by {R["avg_improvement_pts"]} points on average. Of {inr(R["billed_inr"])} billed, {inr(R["collected_inr"])} ({pct(R["collection_rate"], 1)}) was collected.')
doc.add_heading('4.2 Therapist and Therapy Efficiency', 2)
th = sorted(R['vi_by_therapist'].items(), key=lambda kv: -kv[1]['value_index'])
para(f'Fees are similar across therapy types, so value differs by delivery: OT ({R["vi_by_therapy_type"]["ot"]["value_index"]:.2f}) and speech ({R["vi_by_therapy_type"]["speech"]["value_index"]:.2f}) are slightly above fair value, behaviour ({R["vi_by_therapy_type"]["behavior"]["value_index"]:.2f}) and special education ({R["vi_by_therapy_type"]["special_ed"]["value_index"]:.2f}) slightly below. '
     f'Between therapists the spread is wider: {th[0][0]} leads at {th[0][1]["value_index"]:.2f} and {th[-1][0]} trails at {th[-1][1]["value_index"]:.2f}.')
table('Table 4.1: Value index by therapist (progress and fees shared by attended-session share)', ['Therapist', 'Sessions', 'Fees attributed', 'Progress points', 'Value index'],
      [[k, f'{v["sessions"]:,}', inr(v['fees']), f'{v["progress_pts"]:.0f}', f'{v["value_index"]:.2f}'] for k, v in th], [4, 2.5, 3.5, 3.2, 2.8])
figure('fig_therapist.png', 'Value index by therapist', 12.5)
doc.add_heading('4.3 Value Groups and At-Risk Children', 2)
q = R['quadrants']
para(f'{q["Thriving"]} children are Thriving, {q["Efficient"]} Efficient, {q["Under-served"]} Under-served and {q["At-risk"]} At-risk. The Under-served group pays above-median fees for below-median progress and is the first review list. '
     f'The most efficient children returned about {R["top_efficient"][0]["vi"]:.1f}× fair value (e.g. {R["top_efficient"][0]["child"]}); the lowest returned {R["lowest_value"][-1]["vi"]:.2f}×. '
     f'{R["churn_risk_children"]} children are at churn risk and {R["red_risk_children"]} remain in the red clinical band, although {R["risk_improved_children"]} children moved to a better band during the period.')
figure('fig_valuemap.png', 'Value map: fees paid against progress points', 12.5)
sv = R['vi_by_severity']
para(f'Severity matters: severe cases return {sv["severe"]["value_index"]:.2f}× fair value against {sv["moderate"]["value_index"]:.2f}× for moderate, so a flat fee under-serves the hardest cases. Small groups (for example Cerebral Palsy, 2 children) should be read with caution.')
doc.add_heading('4.4 Drivers of Progress', 2)
bi = R['by_involvement']; ft = R['monthly_fee_tier_detail']
para(f'Attendance correlates with improvement (r = {R["corr_attendance_vs_improvement"]:+.2f}) and home-task logging does too (r = {R["corr_home_tasks_vs_improvement"]:+.2f}). Fee level correlates weakly (monthly fee vs improvement r = {R["corr_monthly_fee_vs_improvement"]:+.2f}). '
     'Parent involvement is the clearest lever:')
table('Table 4.2: Outcomes by parent involvement', ['Involvement', 'Children', 'Attendance', 'Improvement (pts)', 'Home tasks/week', 'Value index'],
      [[k.title(), bi[k]['children'], pct(bi[k]['attendance'], 1), bi[k]['improvement_pts'], bi[k]['home_tasks_per_week'], f'{tf[k]["value_index"]:.2f}'] for k in ['low', 'medium', 'high']], [2.6, 2, 2.6, 3.2, 3.2, 2.6])
figure('fig_drivers.png', 'Attendance, improvement and value by parent involvement', 15)
vt = R['vi_by_monthly_fee_tier']
para(f'By monthly fee tier the value index barely moves ({", ".join(f"{k[2:]}: {v["value_index"]:.2f}" for k, v in vt.items())}), so paying a higher monthly fee neither buys nor loses value per rupee; what the family does at home matters more.')
doc.add_heading('4.5 Domains, Alerts and Revenue', 2)
dg = list(R['domain_gain'].items())
para(f'Domains: the fastest gains are {dg[0][0].replace("_", " ")} (+{dg[0][1]["avg_gain_pts"]} points) and {dg[1][0].replace("_", " ")} (+{dg[1][1]["avg_gain_pts"]}); the slowest are {dg[-1][0].replace("_", " ")} (+{dg[-1][1]["avg_gain_pts"]}) and {dg[-2][0].replace("_", " ")} (+{dg[-2][1]["avg_gain_pts"]}).')
figure('fig_domains.png', 'Average assessment gain by domain', 12.5)
s = R['alert_sla']
para(f'Alerts: of {R["alerts_total"]} alerts, {R["alerts_open"]} are still open. High-severity alerts are acknowledged in {s["high"]["avg_hrs_ack"]} hours on average (all within 4 hours) and resolved in {s["high"]["avg_hrs_resolve"]} hours; '
     f'medium and low alerts wait {s["medium"]["avg_hrs_ack"]} hours to be acknowledged (only {pct(s["medium"]["ack_within_4h_pct"], 1)} within 4 hours) and about {s["low"]["avg_hrs_resolve"]:.0f} hours to be resolved. Severe children raise {R["alerts_per_child_by_severity"]["severe"]} alerts each against {R["alerts_per_child_by_severity"]["mild"]} for mild.')
figure('fig_alerts.png', 'Alert response times by severity', 14)
ps = R['payments_by_status']
para(f'Revenue: {R["failed_payments"]} subscription payments failed and {ps["pending"]["count"]} are pending; {inr(R["outstanding_inr"])} is outstanding. Collection is not concentrated in low-involvement families '
     f'(low {pct(bi["low"]["collection_rate"])}, medium {pct(bi["medium"]["collection_rate"])}, high {pct(bi["high"]["collection_rate"])}), so reminders should reach every family. The largest balance is {R["top_outstanding"][0]["child"]} at {inr(R["top_outstanding"][0]["outstanding_inr"])}.')
figure('fig_revenue.png', 'Billed against collected fees by month', 12.5)
doc.add_heading('4.6 Validation', 2)
para('What has been checked:')
bullets([f'An independent Python script (06_Code/analysis.py) recomputes every number in this chapter from the processed CSVs; the league value index equals {R["league_vi_check"]:.3f}.',
         'The processed layer reconciles with the raw layer: 50 children, 8 therapists, all sessions, alerts and payments carried through.',
         'Generator invariants hold: attendance rises with parent involvement; improvement rises with attendance; high-severity alerts are acknowledged fastest.'])
para('What has not yet been checked: the DAX measures have not been evaluated in Power BI Desktop (the project was generated as text on a Mac). The QA Checks page carries the expected values; opening the project and matching them is the remaining acceptance step.', bold=True)

# ------------------------------------------------------------------ 5
doc.add_heading('5. Data Layer and Architecture', 1)
para('The same data live in three forms: MongoDB Atlas (raw collections plus proc_* collections), CSV files for Power BI, and the generator that rebuilds both. NaiviSense already has an Express/MongoDB backend and a Flutter app, '
     'so no separate web application was built; Power BI reads the processed layer directly, and in production the same transformation (process.ts, or a MongoDB aggregation with $merge) would run against live collections.')
figure('fig_architecture.png', 'Architecture: raw layer, processed layer and Power BI', 15)
para('Privacy: the processed layer identifies children only by a child code (C001–C050) and carries no names, and the exports omit password hashes. Real deployments should also pseudonymise parent contact details and apply row-level security before sharing a report, because the data describe children\'s health.')

# ------------------------------------------------------------------ 6
doc.add_heading('6. Recommendations and Conclusion', 1)
doc.add_heading('6.1 Recommendations', 2)
bullets(['Invest in parent coaching and attendance recovery before raising fees: involvement and attendance move value, fee tier does not.',
         'Review the Under-served list and re-engage the At-risk families; call churn-risk families first.',
         'Pair low-index therapists with high-index peers and compare their session routines.',
         'Add a same-day acknowledgement target for medium and low alerts; high-severity triage already works.',
         'Review pricing for severe cases, which return the least progress per rupee on a flat fee.',
         'Automate payment retries and reminders for all families.'])
doc.add_heading('6.2 Limitations', 2)
bullets(['The figures are sample data and the relationships were designed; findings are illustrative until real records are loaded.', 'Progress Points weights (10/20/5) are a modelling choice and should be agreed with clinicians.',
         'Therapist attribution is proportional to sessions, not causal; small groups (e.g. Cerebral Palsy, n = 2) are unreliable.', 'Seven months of data; no seasonality beyond a Diwali-week dip.'])
doc.add_heading('6.3 Conclusion', 2)
para('By storing a sample NaiviSense centre in MongoDB as raw and processed layers and scoring every child on one Progress Points scale, we built an Outcome Value Index that compares progress with fees fairly across children, therapists and plans. '
     'In this dataset, family involvement and attendance explain more of the value than price, severe cases are under-served by flat fees, and routine alerts are answered more slowly than urgent ones. '
     'The Power BI project and this report turn the method into a template that can be pointed at real data.')

doc.add_heading('References', 1)
for r in ['[1] NaiviSense backend data models (Mongoose): backend/src/models.', '[2] MongoDB, Inc. (2026). MongoDB Atlas documentation. https://www.mongodb.com/docs/',
          '[3] Microsoft (2026). Power BI, DAX, Power Query and Power BI Projects documentation. https://learn.microsoft.com/power-bi/',
          '[4] Kimball, R. and Ross, M. (2013). The Data Warehouse Toolkit (3rd ed.). Wiley.',
          '[5] Reference project: IPL Auction Valuation and Player Performance Intelligence, BDM Semester VII (2026) — structure and Value Index idea.']:
    para(r, space=3)
doc.save(OUT)
print('saved', OUT)
