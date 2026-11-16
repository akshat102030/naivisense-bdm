"""Generates the Power BI Project (PBIP) for NaiviSense Outcome Value Intelligence.

    python3 build_pbip.py            ->  ../02_PowerBI/
Open  02_PowerBI/NaiviSense_Outcome_Value.pbip  in Power BI Desktop (Dec 2025+ / PBIR enabled),
then set the DataFolder parameter to the absolute path of ../01_Data.
"""
import csv, json, os, shutil, uuid

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', '01_Data', 'processed')
OUT = os.path.abspath(os.path.join(HERE, '..', '02_PowerBI'))
R = json.load(open(os.path.join(HERE, 'results.json')))
NAME = 'NaiviSense_Outcome_Value'
REPORT = os.path.join(OUT, NAME + '.Report')
MODEL = os.path.join(OUT, NAME + '.SemanticModel')
guid = lambda: str(uuid.uuid4())

# ---------------------------------------------------------------- palette
INK, MUTED, FAINT, GRID, CANVAS, WHITE = '#1F1D1A', '#6E6A62', '#A8A396', '#ECE8DF', '#F6F4EF', '#FFFFFF'
ACCENT = '#2F8F83'
C_THRIVING, C_EFFICIENT, C_UNDER, C_RISK = '#5B7DB1', '#3BA55C', '#E5484D', '#8C8C8C'

# ================================================================= SEMANTIC MODEL
DATE_COLS = {'date', 'month_start', 'week_start', 'assessment_date', 'created_date', 'billing_date', 'target_date', 'enrollment_date', 'enrollment_month'}
TEXT_FORCE = {'child_id', 'therapist_id', 'session_id', 'alert_id', 'payment_id', 'goal_id', 'parent_user_id', 'child_code', 'therapist_name'}
FOLDER = {  # table -> source csv
    t: t for t in ['dim_date', 'dim_child', 'dim_therapist', 'fact_session', 'fact_assessment', 'fact_assessment_domain', 'fact_alert',
                   'fact_payment', 'fact_goal', 'fact_home_engagement_weekly', 'fact_child_therapist', 'agg_child_summary', 'agg_monthly_center']}


def infer(table):
    rows = list(csv.DictReader(open(os.path.join(DATA, table + '.csv'))))
    cols = list(rows[0].keys())
    out = []
    for c in cols:
        vals = [r[c] for r in rows if r[c] != '']
        if c in DATE_COLS: t = 'date'
        elif c in TEXT_FORCE or c.endswith('_id') or not vals: t = 'text'
        else:
            try:
                nums = [float(v) for v in vals]
                t = 'int' if all(float(int(float(v))) == float(v) for v in vals) and all('.' not in v for v in vals) else 'number'
            except ValueError:
                t = 'text'
        out.append((c, t))
    return out


M_TYPE = {'text': 'type text', 'int': 'Int64.Type', 'number': 'type number', 'date': 'type date'}
TM_TYPE = {'text': 'string', 'int': 'int64', 'number': 'double', 'date': 'dateTime'}

CALC_COLS = {  # table -> list of (name, dax, dataType)
    'agg_child_summary': [
        ('Value Group', '''VAR HiFee = agg_child_summary[billed_inr] >= MEDIAN ( agg_child_summary[billed_inr] )
VAR HiPP  = agg_child_summary[progress_points] >= MEDIAN ( agg_child_summary[progress_points] )
RETURN SWITCH ( TRUE (), HiFee && HiPP, "Thriving", NOT HiFee && HiPP, "Efficient", HiFee && NOT HiPP, "Under-served", "At-risk" )''', 'string'),
        ('Fee Tier', '''SWITCH ( TRUE (), agg_child_summary[monthly_fee_inr] < 12000, "1 Under 12k", agg_child_summary[monthly_fee_inr] < 15000, "2 12k-15k", "3 15k and above" )''', 'string'),
    ],
}

MEASURES = [  # (folder, name, dax, format)
    ('Core', 'Students', 'DISTINCTCOUNT ( dim_child[child_id] )', '0'),
    ('Core', 'Therapists', 'DISTINCTCOUNT ( dim_therapist[therapist_id] )', '0'),
    ('Core', 'Sessions Held', 'CALCULATE ( COUNTROWS ( fact_session ), fact_session[is_past] = 1 )', '#,##0'),
    ('Core', 'Sessions Attended', 'CALCULATE ( COUNTROWS ( fact_session ), fact_session[is_attended] = 1 )', '#,##0'),
    ('Core', 'Attendance %', 'DIVIDE ( [Sessions Attended], [Sessions Held] )', '0.0%'),
    ('Core', 'Avg Session Score', 'AVERAGE ( fact_session[avg_session_score] )', '0.00'),
    ('Value', 'Progress Points', 'SUM ( agg_child_summary[progress_points] )', '#,##0.0'),
    ('Value', 'Fees INR', 'SUM ( agg_child_summary[billed_inr] )', '"₹"#,##0'),
    ('Value', 'League Progress Points', 'CALCULATE ( [Progress Points], ALL ( agg_child_summary ), ALL ( dim_child ) )', '#,##0.0'),
    ('Value', 'League Fees INR', 'CALCULATE ( [Fees INR], ALL ( agg_child_summary ), ALL ( dim_child ) )', '"₹"#,##0'),
    ('Value', 'Outcome Value Index', 'DIVIDE ( DIVIDE ( [Progress Points], [League Progress Points] ), DIVIDE ( [Fees INR], [League Fees INR] ) )', '0.00'),
    ('Value', 'Fair Value INR', '[League Fees INR] * DIVIDE ( [Progress Points], [League Progress Points] )', '"₹"#,##0'),
    ('Value', 'Overpay INR', '[Fees INR] - [Fair Value INR]', '"₹"#,##0;-"₹"#,##0'),
    ('Value', 'Therapist Progress Points', 'SUM ( fact_child_therapist[attributed_progress_points] )', '#,##0.0'),
    ('Value', 'Therapist Fees INR', 'SUM ( fact_child_therapist[attributed_fees_inr] )', '"₹"#,##0'),
    ('Value', 'Therapist Value Index',
     '''VAR LeaguePP = CALCULATE ( [Therapist Progress Points], ALL ( fact_child_therapist ), ALL ( dim_therapist ), ALL ( dim_child ) )
VAR LeagueFee = CALCULATE ( [Therapist Fees INR], ALL ( fact_child_therapist ), ALL ( dim_therapist ), ALL ( dim_child ) )
RETURN DIVIDE ( DIVIDE ( [Therapist Progress Points], LeaguePP ), DIVIDE ( [Therapist Fees INR], LeagueFee ) )''', '0.00'),
    ('Value', 'Thriving', 'CALCULATE ( COUNTROWS ( agg_child_summary ), agg_child_summary[Value Group] = "Thriving" )', '0'),
    ('Value', 'Efficient', 'CALCULATE ( COUNTROWS ( agg_child_summary ), agg_child_summary[Value Group] = "Efficient" )', '0'),
    ('Value', 'Under-served', 'CALCULATE ( COUNTROWS ( agg_child_summary ), agg_child_summary[Value Group] = "Under-served" )', '0'),
    ('Value', 'At-risk', 'CALCULATE ( COUNTROWS ( agg_child_summary ), agg_child_summary[Value Group] = "At-risk" )', '0'),
    ('Value', 'Value Group Colour',
     f'SWITCH ( SELECTEDVALUE ( agg_child_summary[Value Group] ), "Thriving", "{C_THRIVING}", "Efficient", "{C_EFFICIENT}", "Under-served", "{C_UNDER}", "{C_RISK}" )', None),
    ('Value', 'Value Index Colour', f'IF ( [Outcome Value Index] >= 1, "{C_EFFICIENT}", "{C_UNDER}" )', None),
    ('Clinical', 'Avg Improvement pts', 'AVERAGE ( agg_child_summary[improvement_pts] )', '0.0'),
    ('Clinical', 'Children Improved %', 'DIVIDE ( CALCULATE ( COUNTROWS ( agg_child_summary ), agg_child_summary[improvement_pts] > 0 ), COUNTROWS ( agg_child_summary ) )', '0%'),
    ('Clinical', 'Avg Overall Score', 'AVERAGE ( fact_assessment[overall_score_pct] )', '0.0'),
    ('Clinical', 'Latest Overall Score', 'AVERAGE ( agg_child_summary[latest_overall_score] )', '0.0'),
    ('Clinical', 'Red-Risk Children', 'CALCULATE ( COUNTROWS ( agg_child_summary ), agg_child_summary[latest_risk] = "red" )', '0'),
    ('Clinical', 'Risk Improved Children', 'SUM ( agg_child_summary[risk_improved] )', '0'),
    ('Clinical', 'Churn-Risk Children', 'SUM ( agg_child_summary[churn_risk] )', '0'),
    ('Clinical', 'Churn-Risk %', 'DIVIDE ( [Churn-Risk Children], COUNTROWS ( agg_child_summary ) )', '0%'),
    ('Clinical', 'Domain Score', 'AVERAGE ( fact_assessment_domain[score] )', '0.0'),
    ('Clinical', 'Domain Gain pts',
     'CALCULATE ( AVERAGE ( fact_assessment_domain[score] ), fact_assessment_domain[is_latest] = 1 ) - CALCULATE ( AVERAGE ( fact_assessment_domain[score] ), fact_assessment_domain[is_initial] = 1 )', '0.0'),
    ('Clinical', 'Domain Latest Score', 'CALCULATE ( AVERAGE ( fact_assessment_domain[score] ), fact_assessment_domain[is_latest] = 1 )', '0.0'),
    ('Clinical', 'Goal Completion %', 'DIVIDE ( SUM ( fact_goal[is_completed] ), COUNTROWS ( fact_goal ) )', '0%'),
    ('Clinical', 'Home Tasks per Week', 'AVERAGE ( fact_home_engagement_weekly[home_tasks_logged] )', '0.0'),
    ('Clinical', 'Meals Logged per Week', 'AVERAGE ( fact_home_engagement_weekly[meals_logged] )', '0.0'),
    ('Alerts', 'Alerts Raised', 'COUNTROWS ( fact_alert )', '0'),
    ('Alerts', 'Open Alerts', 'SUM ( fact_alert[is_open] )', '0'),
    ('Alerts', 'High Severity Alerts', 'CALCULATE ( COUNTROWS ( fact_alert ), fact_alert[severity] = "high" )', '0'),
    ('Alerts', 'Avg Hrs to Acknowledge', 'AVERAGE ( fact_alert[hours_to_acknowledge] )', '0.0'),
    ('Alerts', 'Avg Hrs to Resolve', 'AVERAGE ( fact_alert[hours_to_resolve] )', '0.0'),
    ('Alerts', 'Acknowledged within 4h %',
     'DIVIDE ( CALCULATE ( COUNTROWS ( fact_alert ), fact_alert[hours_to_acknowledge] <= 4, NOT ( ISBLANK ( fact_alert[hours_to_acknowledge] ) ) ), CALCULATE ( COUNTROWS ( fact_alert ), NOT ( ISBLANK ( fact_alert[hours_to_acknowledge] ) ) ) )', '0%'),
    ('Revenue', 'Billed INR', 'CALCULATE ( SUM ( fact_payment[amount_inr] ), fact_payment[payment_type] = "subscription" )', '"₹"#,##0'),
    ('Revenue', 'Collected INR', 'CALCULATE ( SUM ( fact_payment[paid_amount_inr] ), fact_payment[payment_type] = "subscription" )', '"₹"#,##0'),
    ('Revenue', 'Outstanding INR', 'CALCULATE ( SUM ( fact_payment[outstanding_inr] ), fact_payment[payment_type] = "subscription" )', '"₹"#,##0'),
    ('Revenue', 'Collection %', 'DIVIDE ( [Collected INR], [Billed INR] )', '0.0%'),
    ('Revenue', 'Failed Payments', 'CALCULATE ( COUNTROWS ( fact_payment ), fact_payment[status] = "failed", fact_payment[payment_type] = "subscription" )', '0'),
    ('Revenue', 'Payment Count', 'CALCULATE ( COUNTROWS ( fact_payment ), fact_payment[payment_type] = "subscription" )', '0'),
    ('QA', 'League Value Index Check', 'CALCULATE ( [Outcome Value Index], ALL ( dim_child ), ALL ( agg_child_summary ) )', '0.000'),
    ('QA', 'Sessions Rows', 'COUNTROWS ( fact_session )', '#,##0'),
    ('QA', 'Assessment Rows', 'COUNTROWS ( fact_assessment )', '#,##0'),
    ('QA', 'Payment Rows', 'COUNTROWS ( fact_payment )', '#,##0'),
    ('QA', 'Alert Rows', 'COUNTROWS ( fact_alert )', '#,##0'),
]

RELS = [  # many side -> one side
    ('fact_session', 'child_id', 'dim_child', 'child_id'), ('fact_session', 'therapist_id', 'dim_therapist', 'therapist_id'), ('fact_session', 'date', 'dim_date', 'date'),
    ('fact_assessment', 'child_id', 'dim_child', 'child_id'), ('fact_assessment', 'assessment_date', 'dim_date', 'date'),
    ('fact_assessment_domain', 'child_id', 'dim_child', 'child_id'),
    ('fact_alert', 'child_id', 'dim_child', 'child_id'), ('fact_alert', 'created_date', 'dim_date', 'date'),
    ('fact_payment', 'child_id', 'dim_child', 'child_id'), ('fact_payment', 'billing_date', 'dim_date', 'date'),
    ('fact_goal', 'child_id', 'dim_child', 'child_id'),
    ('fact_home_engagement_weekly', 'child_id', 'dim_child', 'child_id'), ('fact_home_engagement_weekly', 'week_start', 'dim_week', 'week_start'),
    ('fact_child_therapist', 'child_id', 'dim_child', 'child_id'), ('fact_child_therapist', 'therapist_id', 'dim_therapist', 'therapist_id'),
]


def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8', newline='\n').write(text)


def tmdl_name(n):
    return f"'{n}'" if any(ch in n for ch in " %-.") else n


def build_model():
    T = '\t'
    w(os.path.join(MODEL, 'definition.pbism'), json.dumps({'version': '4.2', 'settings': {}}, indent=2))
    w(os.path.join(MODEL, 'definition', 'database.tmdl'), 'database\n\tcompatibilityLevel: 1600\n')
    order = list(FOLDER) + ['dim_week', '_Measures']
    refs = ''.join(f"ref table {tmdl_name(t)}\n" for t in order)
    w(os.path.join(MODEL, 'definition', 'model.tmdl'),
      "model Model\n\tculture: en-US\n\tdefaultPowerBIDataSourceVersion: powerBI_V3\n\tdiscourageImplicitMeasures\n\n" + refs + "\nref expression DataFolder\n")
    w(os.path.join(MODEL, 'definition', 'expressions.tmdl'),
      'expression DataFolder = "C:\\Path\\To\\NaiviSense_BDM_Project\\01_Data" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]\n\tlineageTag: ' + guid() + '\n\tqueryGroup: Parameters\n')
    # relationships
    rel = ''
    for a, ac, b, bc in RELS:
        rel += f"relationship {guid()}\n\tfromColumn: {tmdl_name(a)}.{tmdl_name(ac)}\n\ttoColumn: {tmdl_name(b)}.{tmdl_name(bc)}\n\n"
    rel += f"relationship {guid()}\n\tfromCardinality: one\n\tcrossFilteringBehavior: bothDirections\n\tfromColumn: agg_child_summary.child_id\n\ttoColumn: dim_child.child_id\n\n"
    w(os.path.join(MODEL, 'definition', 'relationships.tmdl'), rel)

    for t in FOLDER:
        cols = infer(t)
        s = f"table {tmdl_name(t)}\n\tlineageTag: {guid()}\n\n"
        for c, ty in cols:
            s += f"\tcolumn {tmdl_name(c)}\n\t\tdataType: {TM_TYPE[ty]}\n\t\tlineageTag: {guid()}\n\t\tsummarizeBy: {'none' if ty in ('text', 'date') or c.endswith('_id') or c in ('seq', 'priority') else 'sum'}\n\t\tsourceColumn: {c}\n"
            if ty == 'date': s += "\t\tformatString: yyyy-mm-dd\n"
            s += "\n"
        for name, dax, dt in CALC_COLS.get(t, []):
            lines = dax.split('\n')
            s += f"\tcolumn {tmdl_name(name)} =\n" + ''.join(f"\t\t\t{l}\n" for l in lines)
            s += f"\t\tdataType: {dt}\n\t\tlineageTag: {guid()}\n\t\tsummarizeBy: none\n\n"
        trans = ','.join('{"%s", %s}' % (c, M_TYPE[ty]) for c, ty in cols)
        nonText = [c for c, ty in cols if ty != 'text']
        repl = ('    Cleaned = Table.ReplaceValue(Promoted, "", null, Replacer.ReplaceValue, {%s}),' % ','.join(f'"{c}"' for c in nonText)) if nonText else '    Cleaned = Promoted,'
        s += f"\tpartition {tmdl_name(t)} = m\n\t\tmode: import\n\t\tsource =\n"
        for l in ['let',
                  f'    Source = Csv.Document(File.Contents(DataFolder & "\\processed\\{t}.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),',
                  '    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),', repl,
                  f'    Typed = Table.TransformColumnTypes(Cleaned, {{{trans}}}, "en-US")', 'in', '    Typed']:
            s += f"\t\t\t\t{l}\n"
        s += "\n\tannotation PBI_ResultType = Table\n"
        w(os.path.join(MODEL, 'definition', 'tables', t + '.tmdl'), s)

    w(os.path.join(MODEL, 'definition', 'tables', 'dim_week.tmdl'),
      f"table dim_week\n\tlineageTag: {guid()}\n\n\tcolumn week_start\n\t\tdataType: dateTime\n\t\tformatString: yyyy-mm-dd\n\t\tlineageTag: {guid()}\n\t\tsummarizeBy: none\n\t\tsourceColumn: week_start\n\n"
      "\tpartition dim_week = calculated\n\t\tmode: import\n\t\tsource = DISTINCT ( SELECTCOLUMNS ( dim_date, \"week_start\", dim_date[week_start] ) )\n")

    s = f"table _Measures\n\tlineageTag: {guid()}\n\n"
    for folder, name, dax, fmt in MEASURES:
        lines = dax.split('\n')
        if len(lines) == 1: s += f"\tmeasure {tmdl_name(name)} = {dax}\n"
        else: s += f"\tmeasure {tmdl_name(name)} =\n" + ''.join(f"\t\t\t{l}\n" for l in lines)
        if fmt: s += f"\t\tformatString: {fmt}\n"
        s += f"\t\tdisplayFolder: {folder}\n\t\tlineageTag: {guid()}\n\n"
    s += f"\tcolumn Hidden\n\t\tdataType: int64\n\t\tisHidden\n\t\tlineageTag: {guid()}\n\t\tsummarizeBy: none\n\t\tsourceColumn: Hidden\n\n"
    s += "\tpartition _Measures = calculated\n\t\tmode: import\n\t\tsource = ROW ( \"Hidden\", 1 )\n"
    w(os.path.join(MODEL, 'definition', 'tables', '_Measures.tmdl'), s)


# ================================================================= REPORT (PBIR)
def lit(v): return {'expr': {'Literal': {'Value': v}}}
def S(v): return lit("'" + v.replace("'", "''") + "'")
def D(v): return lit(f'{v}D')
def B(v): return lit('true' if v else 'false')
def col(c): return {'solid': {'color': S(c)}}
def prop(**k): return [{'properties': k}]


class Page:
    def __init__(self, pid, title, hidden=False):
        self.id, self.title, self.visuals, self.z, self.hidden, self.extra = pid, title, [], 1000, hidden, {}

    def add(self, name, x, y, w_, h, visual, container=None, filters=None):
        self.z += 1000
        v = {'$schema': 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json', 'name': f'{self.id}_{name}',
             'position': {'x': x, 'y': y, 'z': self.z, 'height': h, 'width': w_, 'tabOrder': self.z}, 'visual': visual}
        if container: v['visual']['visualContainerObjects'] = container
        if filters: v['filterConfig'] = {'filters': filters}
        self.visuals.append(v)


def field(ref):
    """'Entity.Prop' (column) or '_Measures.Prop' (measure)."""
    ent, p = ref.split('.', 1)
    kind = 'Measure' if ent == '_Measures' else 'Column'
    return {kind: {'Expression': {'SourceRef': {'Entity': ent}}, 'Property': p}}, ent, p


def proj(ref, display=None, active=False):
    f, ent, p = field(ref)
    d = {'field': f, 'queryRef': f'{ent}.{p}', 'nativeQueryRef': p}
    if display: d['displayName'] = display
    if active: d['active'] = True
    return d


def query(roles, sort=None):
    q = {'queryState': {r: {'projections': [proj(x, active=(i == 0 and r in ('Category', 'Rows', 'Columns'))) if isinstance(x, str) else proj(*x) for i, x in enumerate(v)]} for r, v in roles.items()}}
    if sort:
        f, _, _ = field(sort[0]); q['sortDefinition'] = {'sort': [{'field': f, 'direction': sort[1]}], 'isDefaultSort': True}
    return q


def cont(title=None, alt=None, bg=True, link=None):
    c = {'title': prop(show=B(bool(title)), **({'text': S(title), 'fontColor': col(INK), 'fontSize': D(11), 'fontFamily': S('Segoe UI Semibold')} if title else {})),
         'background': prop(show=B(bg), **({'color': col(WHITE), 'transparency': D(0)} if bg else {})),
         'border': prop(show=B(bg), **({'color': col(GRID), 'radius': D(8)} if bg else {}))}
    if alt: c['general'] = prop(altText=S(alt))
    if link: c['visualLink'] = prop(show=B(True), type=S('PageNavigation'), navigationSection=S(link))
    return c


def axis(title=None, grid=False):
    p = dict(show=B(True), labelColor=col(MUTED), fontSize=D(9))
    if title: p.update(showAxisTitle=B(True), titleText=S(title))
    else: p.update(showAxisTitle=B(False))
    if grid: p['gridlineColor'] = col(GRID)
    return prop(**p)


def textbox(pg, name, x, y, w_, h, runs, bg=None, border=None):
    paras = [{'textRuns': [{'value': t, 'textStyle': {'fontFamily': ff, 'fontSize': f'{sz}pt', 'color': c}}]} for t, sz, ff, c in runs]
    c = {'background': prop(show=B(bool(bg)), **({'color': col(bg), 'transparency': D(0)} if bg else {})),
         'border': prop(show=B(bool(border)), **({'color': col(border), 'radius': D(8)} if border else {})),
         'general': prop(altText=S(' '.join(r[0] for r in runs)[:200]))}
    pg.add(name, x, y, w_, h, {'visualType': 'textbox', 'objects': {'general': prop(paragraphs=paras)}}, c)


def card(pg, name, x, y, ref, label, w_=241.6):
    f, ent, p = field(ref)
    pg.add(name, x, y, w_, 62, {'visualType': 'card', 'query': query({'Values': [(ref, label)]}),
           'objects': {'labels': prop(color=col(INK), fontSize=D(22), fontFamily=S('Segoe UI Semibold')),
                       'categoryLabels': prop(show=B(True), color=col(MUTED), fontSize=D(9), fontFamily=S('Segoe UI'))},
           'drillFilterOtherVisuals': True}, cont(alt=label))


def button(pg, name, x, y, w_, h, text, target, fill=None, size=9, color=INK):
    c = cont(bg=False, link=target)
    if fill:
        c['background'] = prop(show=B(True), color=col(fill), transparency=D(0)); c['border'] = prop(show=B(True), color=col(GRID), radius=D(10))
    else:
        c['border'] = prop(show=B(False), radius=D(20))
    pg.add(name, x, y, w_, h, {'visualType': 'actionButton', 'objects': {
        'icon': prop(show=B(False)),
        'text': prop(show=B(True)) + [{'properties': {'text': S(text), 'fontColor': col(color), 'fontSize': D(size), 'fontFamily': S('Segoe UI'),
                                                      'horizontalAlignment': S('center'), 'verticalAlignment': S('middle')}, 'selector': {'id': 'default'}}],
        'fill': prop(show=B(False)), 'outline': prop(show=B(False))}}, c)


def slicer(pg, name, x, y, ref, title, h=64, w_=180):
    pg.add(name, x, y, w_, h, {'visualType': 'slicer', 'query': query({'Values': [ref]}), 'objects': {
        'data': prop(mode=S('Dropdown')),
        'header': prop(show=B(True), fontColor=col(MUTED), text=S(title)),
        'items': prop(fontColor=col(INK)),
        'selection': prop(selectAllCheckboxEnabled=B(True))}}, cont(bg=True))


def chart(pg, name, x, y, w_, h, vtype, roles, title, xt=None, yt=None, sort=None, refline=None, colour_measure=None, labels=True, trend=False, legend=False):
    obj = {'categoryAxis': axis(xt), 'valueAxis': axis(yt, grid=True)}
    if labels and vtype not in ('scatterChart',): obj['labels'] = prop(show=B(True), color=col(INK), fontSize=D(8))
    if colour_measure:
        obj['dataPoint'] = [{'properties': {'fill': {'solid': {'color': {'expr': {'Measure': {'Expression': {'SourceRef': {'Entity': '_Measures'}}, 'Property': colour_measure}}}}}},
                             'selector': {'data': [{'dataViewWildcard': {'matchingOption': 1}}]}}]
    if refline is not None:
        obj['y1AxisReferenceLine'] = prop(show=B(True), value=D(refline), lineColor=col(INK), style=S('dashed'), transparency=D(20), width=D(1),
                                          displayName=S('Fair value 1.00'), dataLabelShow=B(True), dataLabelText=S('Name'), dataLabelColor=col(INK))
    if vtype == 'scatterChart':
        obj['categoryLabels'] = prop(show=B(False)); obj['bubbles'] = prop(bubbleSize=D(-10))
        if trend: obj['trend'] = [{'properties': {'show': B(True), 'lineColor': col(INK), 'style': S('dashed'), 'transparency': D(30)}, 'selector': {'id': '1'}}]
    if legend: obj['legend'] = prop(show=B(True), position=S('Top'), labelColor=col(MUTED))
    pg.add(name, x, y, w_, h, {'visualType': vtype, 'query': query(roles, sort), 'objects': obj, 'drillFilterOtherVisuals': True}, cont(title=title, alt=title))


def table(pg, name, x, y, w_, h, refs, title, sort=None, cat_filter=None):
    obj = {'columnHeaders': prop(fontColor=col(MUTED), backColor=col(WHITE), fontSize=D(9), fontFamily=S('Segoe UI Semibold')),
           'values': prop(fontColorPrimary=col(INK), backColorPrimary=col(WHITE), fontColorSecondary=col(INK), backColorSecondary=col('#FAF8F3'), fontSize=D(9)),
           'grid': prop(gridHorizontalColor=col(GRID))}
    flt = None
    if cat_filter:
        ref, val = cat_filter; f, ent, p = field(ref)
        flt = [{'name': f'{name}_f', 'field': f, 'type': 'Categorical', 'filter': {'Version': 2, 'From': [{'Name': 's', 'Entity': ent, 'Type': 0}],
                'Where': [{'Condition': {'In': {'Expressions': [{'Column': {'Expression': {'SourceRef': {'Source': 's'}}, 'Property': p}}], 'Values': [[{'Literal': {'Value': val}}]]}}}]}}]
    pg.add(name, x, y, w_, h, {'visualType': 'tableEx', 'query': query({'Values': refs}, sort), 'objects': obj, 'drillFilterOtherVisuals': True}, cont(title=title, alt=title), filters=flt)


def matrix(pg, name, x, y, w_, h, rows, colsr, vals, title):
    obj = {'columnHeaders': prop(fontColor=col(MUTED), backColor=col(WHITE), fontSize=D(9), fontFamily=S('Segoe UI Semibold')),
           'rowHeaders': prop(fontColor=col(INK), backColor=col(WHITE), fontSize=D(9), fontFamily=S('Segoe UI Semibold')),
           'values': prop(fontColorPrimary=col(INK), backColorPrimary=col(WHITE), fontColorSecondary=col(INK), backColorSecondary=col(WHITE), fontSize=D(9)),
           'grid': prop(gridHorizontalColor=col(GRID))}
    pg.add(name, x, y, w_, h, {'visualType': 'pivotTable', 'query': query({'Rows': rows, 'Columns': colsr, 'Values': vals}), 'objects': obj}, cont(title=title, alt=title))


NAV = [('home', 'Home'), ('therapy', 'Therapy'), ('valuemap', 'Value Map'), ('atrisk', 'At-Risk'), ('drivers', 'Drivers'), ('domains', 'Domains'), ('alerts', 'Alerts'), ('revenue', 'Revenue'), ('methodology', 'Method')]


def chrome(pg, headline, sub, sowhat=None):
    textbox(pg, 'navbg', 0, 0, 1280, 72, [('', 1, 'Segoe UI', WHITE)], bg=WHITE)
    textbox(pg, 'brand', 16, 14, 280, 44, [('NaiviSense', 15, 'Segoe UI Semibold', INK), ('Therapy Outcome Value Intelligence', 8, 'Segoe UI', MUTED)])
    for i, (pid, label) in enumerate(NAV):
        button(pg, f'nav_{pid}', 300 + i * 88, 20, 84, 32, label, pid, fill=('#E3F1EE' if pid == pg.id else None))
    textbox(pg, 'headline', 16, 80, 1248, 44, [(headline, 14, 'Segoe UI Semibold', INK), (sub, 9, 'Segoe UI', MUTED)])
    if sowhat:
        textbox(pg, 'sowhat', 16, 664, 1248, 44, [('So what: ' + sowhat, 10, 'Segoe UI Semibold', INK)], bg='#E3F1EE', border=GRID)


def kpis(pg, items, y=130):
    n = len(items); wd = (1248 - (n - 1) * 8) / n
    for i, (ref, label) in enumerate(items): card(pg, f'kpi{i}', 16 + i * (wd + 8), y, ref, label, w_=wd)


def build_pages():
    pages = []
    m = R
    vi_t = m['vi_by_therapy_type']; vi_i = m['vi_by_involvement']; q = m['quadrants']
    best_th = max(m['vi_by_therapist'].items(), key=lambda kv: kv[1]['value_index']); worst_th = min(m['vi_by_therapist'].items(), key=lambda kv: kv[1]['value_index'])
    sla = m['alert_sla']

    # ---------------- Home
    p = Page('home', 'Home'); pages.append(p)
    chrome(p, 'Which therapy rupees actually moved a child forward?', f'{m["students"]} children · {m["therapists"]} therapists · May–Nov 2026 · sample data prepared for Naivedyam Child Development Center')
    kpis(p, [('_Measures.Students', 'Children enrolled'), ('_Measures.Attendance %', 'Attendance'), ('_Measures.Avg Improvement pts', 'Avg improvement (pts)'),
             ('_Measures.Collection %', 'Fees collected'), ('_Measures.Churn-Risk Children', 'Children at churn risk')])
    cards = [('therapy', 'Q1 · Which therapist delivers the most progress per rupee?'), ('valuemap', 'Q2 · Which children are Thriving, Efficient, Under-served or At-risk?'),
             ('drivers', 'Q3 · Does attendance or parent involvement drive progress?'), ('domains', 'Q4 · Which developmental domains improve fastest?'),
             ('alerts', 'Q5 · Are safety alerts acknowledged and resolved in time?'), ('revenue', 'Q6 · Where does revenue leak, and who is behind?')]
    for i, (t, txt) in enumerate(cards):
        button(p, f'q{i}', 16 + (i % 3) * 418, 214 + (i // 3) * 96, 410, 88, txt, t, fill=WHITE, size=11)
    textbox(p, 'idea', 16, 416, 1248, 236, [('The one idea', 12, 'Segoe UI Semibold', INK),
            ('Progress Points = 10 × assessment gain + 20 × session-score gain + 5 × goals completed.', 10, 'Segoe UI', INK),
            ('Outcome Value Index = (child\'s share of centre progress) ÷ (child\'s share of centre fees).', 10, 'Segoe UI', INK),
            ('1.00 is fair value. Above 1 the family got more progress than the fees paid; below 1 less.', 10, 'Segoe UI', INK),
            ('Value groups (median fee × median progress): Thriving · Efficient · Under-served · At-risk.', 10, 'Segoe UI', INK),
            ('Findings in one line: parent involvement moves value more than fee level; attendance tracks improvement; high-severity alerts are acknowledged fast, routine ones are not.', 10, 'Segoe UI Semibold', ACCENT)], bg=WHITE, border=GRID)

    # ---------------- Therapy (Q1)
    p = Page('therapy', 'Therapy'); pages.append(p)
    chrome(p, f'{best_th[0]} leads at {best_th[1]["value_index"]:.2f}× fair value; {worst_th[0]} trails at {worst_th[1]["value_index"]:.2f}×',
           'Q1 · Which therapist and therapy type delivers the most progress per rupee? (progress and fees shared by attended-session share)',
           'Coach low-index therapists on the structured routines of high-index peers; fees are similar across types, so value differs by delivery, not price.')
    kpis(p, [('_Measures.Therapists', 'Therapists'), ('_Measures.Sessions Attended', 'Sessions attended'), ('_Measures.Therapist Progress Points', 'Progress points'),
             ('_Measures.Therapist Fees INR', 'Fees attributed'), ('_Measures.Avg Session Score', 'Avg session score (1-10)')])
    slicer(p, 'type', 24, 204, 'dim_therapist.specialty', 'Therapy type')
    chart(p, 'vi_ther', 224, 204, 520, 220, 'clusteredColumnChart', {'Category': ['dim_therapist.therapist_name'], 'Y': ['_Measures.Therapist Value Index']},
          'Value Index by therapist (1.00 = fair)', refline=1, sort=('_Measures.Therapist Value Index', 'Descending'), colour_measure=None)
    chart(p, 'vi_type', 754, 204, 510, 220, 'clusteredColumnChart', {'Category': ['fact_child_therapist.therapy_type'], 'Y': ['_Measures.Therapist Value Index']},
          'Value Index by therapy type', refline=1)
    table(p, 'tbl', 224, 434, 1040, 222, ['dim_therapist.therapist_name', 'dim_therapist.specialty', 'dim_therapist.caseload_children', '_Measures.Sessions Attended',
          '_Measures.Therapist Progress Points', '_Measures.Therapist Fees INR', '_Measures.Therapist Value Index'], 'Therapist scorecard', sort=('_Measures.Therapist Value Index', 'Descending'))

    # ---------------- Value map (Q2)
    p = Page('valuemap', 'Value Map'); pages.append(p)
    chrome(p, f'{q["Thriving"]} Thriving · {q["Efficient"]} Efficient · {q["Under-served"]} Under-served · {q["At-risk"]} At-risk',
           'Q2 · Each dot is one child: fees paid (left→right) against progress points (bottom→top). Groups split at the median fee and median progress.',
           'Keep Thriving and Efficient plans; review the Under-served list (high fees, low progress) and re-engage the At-risk families before they drop out.')
    kpis(p, [('_Measures.Thriving', 'Thriving'), ('_Measures.Efficient', 'Efficient'), ('_Measures.Under-served', 'Under-served'), ('_Measures.At-risk', 'At-risk'),
             ('_Measures.League Value Index Check', 'Centre value index')])
    slicer(p, 'dx', 24, 204, 'dim_child.primary_diagnosis', 'Diagnosis'); slicer(p, 'sev', 24, 274, 'dim_child.severity', 'Severity')
    slicer(p, 'inv', 24, 344, 'dim_child.parent_involvement', 'Parent involvement'); slicer(p, 'grp', 24, 414, 'agg_child_summary.Value Group', 'Value group')
    chart(p, 'scatter', 224, 204, 700, 452, 'scatterChart', {'Category': ['agg_child_summary.child_code'], 'X': ['_Measures.Fees INR'], 'Y': ['_Measures.Progress Points'],
          'Size': ['_Measures.Sessions Attended'], 'Tooltips': ['_Measures.Outcome Value Index', '_Measures.Overpay INR']}, 'Fees paid vs progress points', xt='Fees paid (₹)', yt='Progress points',
          colour_measure='Value Group Colour')
    table(p, 'tbl', 934, 204, 330, 452, ['agg_child_summary.child_code', 'agg_child_summary.Value Group', '_Measures.Outcome Value Index'], 'Children by value index', sort=('_Measures.Outcome Value Index', 'Descending'))

    # ---------------- At-risk
    p = Page('atrisk', 'At-Risk'); pages.append(p)
    chrome(p, f'{m["churn_risk_children"]} children at churn risk · {m["red_risk_children"]} still in the red clinical band',
           'Q2 · Named lists: who to protect, who to review. Churn risk = attendance < 70%, or red band with < 3 pts gain, or 2+ failed payments.',
           'Call the churn-risk families this week; review the plans of Under-served children before the next billing cycle.')
    kpis(p, [('_Measures.Churn-Risk Children', 'Churn-risk children'), ('_Measures.Red-Risk Children', 'Red-band children'), ('_Measures.Risk Improved Children', 'Moved to a better band'),
             ('_Measures.Open Alerts', 'Open alerts'), ('_Measures.Outstanding INR', 'Outstanding fees')])
    cols = ['agg_child_summary.child_code', 'agg_child_summary.attendance_rate', 'agg_child_summary.improvement_pts', 'agg_child_summary.latest_risk', '_Measures.Outcome Value Index']
    table(p, 'churn', 16, 204, 410, 450, cols, 'Churn-risk children', cat_filter=('agg_child_summary.churn_risk', '1L'))
    table(p, 'under', 436, 204, 410, 450, cols, 'Under-served (high fee, low progress)', cat_filter=('agg_child_summary.Value Group', "'Under-served'"), sort=('_Measures.Outcome Value Index', 'Ascending'))
    table(p, 'eff', 856, 204, 408, 450, cols, 'Efficient (low fee, high progress)', cat_filter=('agg_child_summary.Value Group', "'Efficient'"), sort=('_Measures.Outcome Value Index', 'Descending'))

    # ---------------- Drivers (Q3)
    p = Page('drivers', 'Drivers'); pages.append(p)
    hi, lo = vi_i['high'], vi_i['low']
    chrome(p, f'High-involvement families get {hi["value_index"]:.2f}× fair value; low-involvement get {lo["value_index"]:.2f}×',
           f'Q3 · Attendance vs improvement r = {m["corr_attendance_vs_improvement"]:+.2f}; monthly fee vs improvement r = {m["corr_monthly_fee_vs_improvement"]:+.2f}',
           'Spend effort on parent coaching and attendance recovery, not on higher-priced plans: involvement moves value far more than fee level does.')
    kpis(p, [('_Measures.Attendance %', 'Attendance'), ('_Measures.Avg Improvement pts', 'Avg improvement (pts)'), ('_Measures.Home Tasks per Week', 'Home tasks / week'),
             ('_Measures.Meals Logged per Week', 'Meals logged / week'), ('_Measures.Outcome Value Index', 'Value index (selection)')])
    slicer(p, 'dx', 24, 204, 'dim_child.primary_diagnosis', 'Diagnosis'); slicer(p, 'sev', 24, 274, 'dim_child.severity', 'Severity'); slicer(p, 'age', 24, 344, 'dim_child.age_band', 'Age band')
    chart(p, 'scatter', 224, 204, 520, 220, 'scatterChart', {'Category': ['agg_child_summary.child_code'], 'X': ['_Measures.Attendance %'], 'Y': ['_Measures.Avg Improvement pts']},
          'Attendance vs improvement (dashed = trend)', xt='Attendance rate', yt='Improvement (pts)', trend=True)
    chart(p, 'inv_vi', 754, 204, 510, 220, 'clusteredColumnChart', {'Category': ['dim_child.parent_involvement'], 'Y': ['_Measures.Outcome Value Index']}, 'Value index by parent involvement', refline=1)
    chart(p, 'inv_att', 224, 434, 340, 222, 'clusteredColumnChart', {'Category': ['dim_child.parent_involvement'], 'Y': ['_Measures.Attendance %']}, 'Attendance by parent involvement')
    chart(p, 'inv_imp', 574, 434, 340, 222, 'clusteredColumnChart', {'Category': ['dim_child.parent_involvement'], 'Y': ['_Measures.Avg Improvement pts']}, 'Improvement by parent involvement')
    chart(p, 'tier', 924, 434, 340, 222, 'clusteredColumnChart', {'Category': ['agg_child_summary.Fee Tier'], 'Y': ['_Measures.Outcome Value Index']}, 'Value index by monthly fee tier', refline=1)

    # ---------------- Domains (Q4)
    p = Page('domains', 'Domains'); pages.append(p)
    top = list(m['domain_gain'].items())
    chrome(p, f'Fastest gains: {top[0][0].replace("_", " ")} (+{top[0][1]["avg_gain_pts"]}) and {top[1][0].replace("_", " ")} (+{top[1][1]["avg_gain_pts"]}); slowest: {top[-1][0].replace("_", " ")} (+{top[-1][1]["avg_gain_pts"]})',
           'Q4 · Average points gained per assessment domain between the initial and the latest assessment (0–100 scale).',
           'Add targeted therapy blocks for the slowest domains; check whether a domain is slow because it is untreated or because it is hard to move.')
    kpis(p, [('_Measures.Latest Overall Score', 'Avg latest score'), ('_Measures.Avg Improvement pts', 'Avg improvement (pts)'), ('_Measures.Children Improved %', 'Children improved'),
             ('_Measures.Goal Completion %', 'Goals completed'), ('_Measures.Risk Improved Children', 'Moved to a better band')])
    slicer(p, 'dx', 24, 204, 'dim_child.primary_diagnosis', 'Diagnosis'); slicer(p, 'sev', 24, 274, 'dim_child.severity', 'Severity')
    chart(p, 'gain', 224, 204, 520, 452, 'clusteredBarChart', {'Category': ['fact_assessment_domain.domain'], 'Y': ['_Measures.Domain Gain pts']}, 'Average gain by domain (points)', sort=('_Measures.Domain Gain pts', 'Descending'))
    chart(p, 'trend', 754, 204, 510, 220, 'lineChart', {'Category': ['fact_assessment.month_start'], 'Y': ['_Measures.Avg Overall Score']}, 'Average overall assessment score by month', labels=False)
    matrix(p, 'mx', 754, 434, 510, 222, ['fact_assessment_domain.domain_group'], ['dim_child.severity'], ['_Measures.Domain Gain pts'], 'Domain-group gain by severity')

    # ---------------- Alerts (Q5)
    p = Page('alerts', 'Alerts'); pages.append(p)
    chrome(p, f'High-severity alerts are acknowledged in {sla["high"]["avg_hrs_ack"]} h; medium/low take about {sla["medium"]["avg_hrs_ack"]} h',
           f'Q5 · {m["alerts_total"]} alerts raised; {m["alerts_open"]} still open. Resolution takes {sla["high"]["avg_hrs_resolve"]} h (high) vs {sla["low"]["avg_hrs_resolve"]} h (low).',
           'Severe cases are triaged well; routine alerts wait too long. Set a same-day acknowledgement target for medium and low alerts.')
    kpis(p, [('_Measures.Alerts Raised', 'Alerts raised'), ('_Measures.Open Alerts', 'Open alerts'), ('_Measures.High Severity Alerts', 'High severity'),
             ('_Measures.Avg Hrs to Acknowledge', 'Avg hrs to acknowledge'), ('_Measures.Avg Hrs to Resolve', 'Avg hrs to resolve')])
    slicer(p, 'sev', 24, 204, 'fact_alert.severity', 'Severity'); slicer(p, 'type', 24, 274, 'fact_alert.alert_type', 'Alert type')
    chart(p, 'ack', 224, 204, 340, 220, 'clusteredColumnChart', {'Category': ['fact_alert.severity'], 'Y': ['_Measures.Avg Hrs to Acknowledge']}, 'Hours to acknowledge, by severity')
    chart(p, 'res', 574, 204, 340, 220, 'clusteredColumnChart', {'Category': ['fact_alert.severity'], 'Y': ['_Measures.Avg Hrs to Resolve']}, 'Hours to resolve, by severity')
    chart(p, 'type', 924, 204, 340, 220, 'clusteredBarChart', {'Category': ['fact_alert.alert_type'], 'Y': ['_Measures.Alerts Raised']}, 'Alerts by type', sort=('_Measures.Alerts Raised', 'Descending'))
    chart(p, 'month', 224, 434, 440, 222, 'columnChart', {'Category': ['fact_alert.month_start'], 'Y': ['_Measures.Alerts Raised']}, 'Alerts per month')
    table(p, 'open', 674, 434, 590, 222, ['fact_alert.created_date', 'fact_alert.alert_type', 'fact_alert.severity', 'fact_alert.source', 'fact_alert.status'], 'Open alerts', sort=('fact_alert.created_date', 'Ascending'), cat_filter=('fact_alert.is_open', '1L'))

    # ---------------- Revenue (Q6)
    p = Page('revenue', 'Revenue'); pages.append(p)
    st_ = m['payments_by_status']
    chrome(p, f'₹{m["collected_inr"]/1e5:.1f} L collected of ₹{m["billed_inr"]/1e5:.1f} L billed ({m["collection_rate"]:.0%}); ₹{m["outstanding_inr"]/1e5:.1f} L outstanding',
           f'Q6 · {m["failed_payments"]} failed subscription payments. Collection by parent involvement: low {m["by_involvement"]["low"]["collection_rate"]:.0%}, medium {m["by_involvement"]["medium"]["collection_rate"]:.0%}, high {m["by_involvement"]["high"]["collection_rate"]:.0%}.',
           'Collection gaps are spread across involvement levels (not concentrated in low-involvement families), so automate retries and reminders for every family.')
    kpis(p, [('_Measures.Billed INR', 'Billed'), ('_Measures.Collected INR', 'Collected'), ('_Measures.Outstanding INR', 'Outstanding'), ('_Measures.Collection %', 'Collection rate'), ('_Measures.Failed Payments', 'Failed payments')])
    slicer(p, 'inv', 24, 204, 'dim_child.parent_involvement', 'Parent involvement'); slicer(p, 'dx', 24, 274, 'dim_child.primary_diagnosis', 'Diagnosis')
    chart(p, 'month', 224, 204, 520, 220, 'clusteredColumnChart', {'Category': ['fact_payment.month_start'], 'Y': ['_Measures.Billed INR', '_Measures.Collected INR']}, 'Billed vs collected by month', labels=False, legend=True)
    chart(p, 'status', 754, 204, 510, 220, 'hundredPercentStackedBarChart', {'Category': ['fact_payment.month_start'], 'Series': ['fact_payment.status'], 'Y': ['_Measures.Payment Count']}, 'Payment status mix by month', labels=False, legend=True)
    chart(p, 'inv', 224, 434, 340, 222, 'clusteredColumnChart', {'Category': ['dim_child.parent_involvement'], 'Y': ['_Measures.Outstanding INR']}, 'Outstanding by parent involvement')
    table(p, 'out', 574, 434, 690, 222, ['agg_child_summary.child_code', 'dim_child.parent_involvement', 'agg_child_summary.billed_inr', 'agg_child_summary.collected_inr', 'agg_child_summary.outstanding_inr'],
          'Largest outstanding balances', sort=('agg_child_summary.outstanding_inr', 'Descending'))

    # ---------------- Profile (drill-through)
    p = Page('profile', 'Student Profile', hidden=True); pages.append(p)
    p.extra = {'drill': True}
    chrome(p, 'Student profile', 'Right-click a child on Value Map, At-Risk or Therapy and choose Drill through → Student Profile.')
    kpis(p, [('_Measures.Attendance %', 'Attendance'), ('_Measures.Avg Improvement pts', 'Improvement (pts)'), ('_Measures.Outcome Value Index', 'Value index'),
             ('_Measures.Open Alerts', 'Open alerts'), ('_Measures.Outstanding INR', 'Outstanding fees')])
    chart(p, 'score', 16, 204, 400, 220, 'lineChart', {'Category': ['fact_assessment.assessment_date'], 'Y': ['_Measures.Avg Overall Score']}, 'Overall assessment score over time', labels=False)
    chart(p, 'sess', 426, 204, 400, 220, 'columnChart', {'Category': ['fact_session.week_start'], 'Y': ['_Measures.Avg Session Score']}, 'Session score by week', labels=False)
    chart(p, 'dom', 836, 204, 428, 220, 'clusteredBarChart', {'Category': ['fact_assessment_domain.domain'], 'Y': ['_Measures.Domain Latest Score']}, 'Latest domain scores', labels=False)
    table(p, 'goals', 16, 434, 620, 222, ['fact_goal.title', 'fact_goal.status', 'fact_goal.target_date'], 'Goals')
    table(p, 'alerts', 646, 434, 618, 222, ['fact_alert.created_date', 'fact_alert.alert_type', 'fact_alert.severity', 'fact_alert.status'], 'Alerts')

    # ---------------- Methodology
    p = Page('methodology', 'Method'); pages.append(p)
    chrome(p, 'How value is measured', 'Definitions, data sources and limitations')
    textbox(p, 'defs', 16, 134, 612, 520, [('Metrics', 12, 'Segoe UI Semibold', INK),
            ('Progress Points = 10 × (latest − initial overall assessment score) + 20 × (second-half − first-half average session score) + 5 × goals completed, floored at 0.', 10, 'Segoe UI', INK),
            ('Outcome Value Index = (child progress ÷ centre progress) ÷ (child fees ÷ centre fees). 1.00 = fair value.', 10, 'Segoe UI', INK),
            ('Fair Value = centre fees × child\'s share of progress. Overpay = fees − fair value.', 10, 'Segoe UI', INK),
            ('Value groups use the median fee and median progress: Thriving (high/high), Efficient (low fee, high progress), Under-served (high fee, low progress), At-risk (low/low).', 10, 'Segoe UI', INK),
            ('Therapist value shares each child\'s progress and fees by the therapist\'s share of attended sessions.', 10, 'Segoe UI', INK),
            ('Churn risk = attendance < 70%, or red band with < 3 pts gain, or 2+ failed payments.', 10, 'Segoe UI', INK)], bg=WHITE, border=GRID)
    textbox(p, 'src', 636, 134, 628, 520, [('Data and limits', 12, 'Segoe UI Semibold', INK),
            ('Source: NaiviSense MongoDB collections (users, children, sessions, attendances, assessments, alerts, payments, goals, meal and home-task logs).', 10, 'Segoe UI', INK),
            ('All records are sample data prepared for Naivedyam Child Development Center (50 children, 8 therapists, 4 May – 15 Nov 2026). Real, anonymised records will replace them.', 10, 'Segoe UI', INK),
            ('Raw layer: 01_Data/raw. Processed star schema: 01_Data/processed, rebuilt by the scripts in the generator folder.', 10, 'Segoe UI', INK),
            ('Fees are subscription invoices only. Billing starts at the later of enrolment and 4 May 2026.', 10, 'Segoe UI', INK),
            ('Limitations: relationships in the sample data are designed, not discovered; Progress Points weights are a modelling choice; therapist attribution is proportional to sessions, not causal.', 10, 'Segoe UI', INK),
            ('Model: star schema, 13 tables, many-to-one relationships, 53 DAX measures in the _Measures table.', 10, 'Segoe UI', INK)], bg=WHITE, border=GRID)

    # ---------------- QA
    p = Page('qa', 'QA Checks', hidden=True); pages.append(p)
    chrome(p, 'QA checks: model numbers vs independent Python re-computation', 'Expected values are printed by 06_Code/analysis.py')
    kpis(p, [('_Measures.Students', f'Children (expect {m["students"]})'), ('_Measures.Therapists', f'Therapists (expect {m["therapists"]})'),
             ('_Measures.League Value Index Check', 'League value index (expect 1.000)'), ('_Measures.Sessions Attended', f'Sessions attended (expect {m["sessions_attended"]:,})'),
             ('_Measures.Attendance %', f'Attendance (expect {m["attendance_rate"]:.1%})')])
    kpis(p, [('_Measures.Billed INR', f'Billed (expect ₹{m["billed_inr"]:,.0f})'), ('_Measures.Collected INR', f'Collected (expect ₹{m["collected_inr"]:,.0f})'),
             ('_Measures.Alerts Raised', f'Alerts (expect {m["alerts_total"]})'), ('_Measures.Avg Improvement pts', f'Avg improvement (expect {m["avg_improvement_pts"]})'),
             ('_Measures.Progress Points', f'Progress points (expect {m["total_progress_points"]})')], y=204)
    return pages


def build_report():
    base = os.path.join(REPORT, 'definition')
    w(os.path.join(REPORT, 'definition.pbir'), json.dumps({'version': '4.0', 'datasetReference': {'byPath': {'path': f'../{NAME}.SemanticModel'}}}, indent=2))
    w(os.path.join(base, 'version.json'), json.dumps({'$schema': 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json', 'version': '2.0.0'}, indent=2))
    w(os.path.join(base, 'report.json'), json.dumps({
        '$schema': 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.3.0/schema.json',
        'themeCollection': {'baseTheme': {'name': 'CY24SU10', 'reportVersionAtImport': {'visual': '1.8.95', 'report': '2.0.95', 'page': '1.3.95'}, 'type': 'SharedResources'},
                            'customTheme': {'name': 'NaiviSense_Light.json', 'reportVersionAtImport': {'visual': '1.8.95', 'report': '2.0.95', 'page': '1.3.95'}, 'type': 'RegisteredResources'}},
        'resourcePackages': [{'name': 'RegisteredResources', 'type': 'RegisteredResources', 'items': [{'name': 'NaiviSense_Light.json', 'path': 'NaiviSense_Light.json', 'type': 'CustomTheme'}]}],
        'settings': {'useStylableVisualContainerHeader': True, 'exportDataMode': 'AllowSummarized', 'defaultDrillFilterOtherVisuals': True, 'allowChangeFilterTypes': True, 'useEnhancedTooltips': True}}, indent=2))
    theme = {'name': 'NaiviSense Light', 'dataColors': [ACCENT, C_THRIVING, C_EFFICIENT, '#F2B84B', C_UNDER, '#7B61C9', C_RISK, '#E57BAA'], 'foreground': INK,
             'foregroundNeutralSecondary': MUTED, 'foregroundNeutralTertiary': FAINT, 'background': WHITE, 'backgroundLight': '#FAF8F3', 'backgroundNeutral': GRID, 'tableAccent': ACCENT,
             'good': C_EFFICIENT, 'neutral': '#F2B84B', 'bad': C_UNDER, 'maximum': C_EFFICIENT, 'center': WHITE, 'minimum': C_UNDER, 'null': '#C9C5BC',
             'textClasses': {'callout': {'fontSize': 26, 'fontFace': 'Segoe UI Semibold', 'color': INK}, 'title': {'fontSize': 12, 'fontFace': 'Segoe UI Semibold', 'color': INK},
                             'header': {'fontSize': 11, 'fontFace': 'Segoe UI Semibold', 'color': INK}, 'label': {'fontSize': 9, 'fontFace': 'Segoe UI', 'color': MUTED}}}
    w(os.path.join(REPORT, 'StaticResources', 'RegisteredResources', 'NaiviSense_Light.json'), json.dumps(theme, indent=2))
    pages = build_pages()
    w(os.path.join(base, 'pages', 'pages.json'), json.dumps({'$schema': 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json',
                                                           'pageOrder': [p.id for p in pages], 'activePageName': 'home'}, indent=2))
    for p in pages:
        pj = {'$schema': 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json', 'name': p.id, 'displayName': p.title,
              'displayOption': 'FitToPage', 'height': 720, 'width': 1280,
              'objects': {'background': prop(color=col(CANVAS), transparency=D(0)), 'outspace': prop(color=col(CANVAS))}}
        if p.extra.get('drill'):
            ref = {'Column': {'Expression': {'SourceRef': {'Entity': 'dim_child'}}, 'Property': 'child_code'}}
            pj['pageBinding'] = {'name': 'profile_binding', 'type': 'Drillthrough', 'parameters': [{'name': 'profile_param', 'boundFilter': 'profile_drill', 'fieldExpr': ref}]}
            pj['filterConfig'] = {'filters': [{'name': 'profile_drill', 'field': ref, 'type': 'Categorical', 'howCreated': 'Drillthrough'}]}
        if p.hidden: pj['visibility'] = 'HiddenInViewMode'
        w(os.path.join(base, 'pages', p.id, 'page.json'), json.dumps(pj, indent=2, ensure_ascii=False))
        for v in p.visuals:
            w(os.path.join(base, 'pages', p.id, 'visuals', v['name'], 'visual.json'), json.dumps(v, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    build_model(); build_report()
    w(os.path.join(OUT, NAME + '.pbip'), json.dumps({'version': '1.0', 'artifacts': [{'report': {'path': NAME + '.Report'}}], 'settings': {'enableAutoRecovery': True}}, indent=2))
    md = ['# DAX measures (generated from build_pbip.py, so this file always matches the model)\n',
          'All measures live in the `_Measures` table. Calculated columns are on `agg_child_summary`.\n']
    for name, dax, dt in CALC_COLS['agg_child_summary']:
        md.append(f"## Calculated column: `agg_child_summary[{name}]`\n```DAX\n{dax}\n```\n")
    cur = None
    for folder, name, dax, fmt in MEASURES:
        if folder != cur: md.append(f"\n## {folder}\n"); cur = folder
        md.append(f"### {name}\n```DAX\n{name} =\n{dax}\n```\nFormat: `{fmt or 'text (colour hex)'}`\n")
    w(os.path.join(OUT, 'DAX_Measures.md'), '\n'.join(md))
    w(os.path.join(OUT, 'README_Open_In_PowerBI.md'), """# Open the NaiviSense Power BI project

1. Install **Power BI Desktop** (Windows). Enable *File > Options > Preview features > Power BI Project (.pbip) save option* and *Store reports using enhanced metadata format (PBIR)* if your version asks.
2. Double-click `NaiviSense_Outcome_Value.pbip`.
3. Home > Transform data > Manage parameters > set **DataFolder** to the absolute path of `../01_Data` (for example `C:\\Projects\\NaiviSense_BDM_Project\\01_Data`). No trailing slash.
4. Close & Apply. All 13 tables load from `01_Data/processed/*.csv`.
5. Open **Model view**: check the star schema (15 relationships; `agg_child_summary` <-> `dim_child` is one-to-one, both directions).
6. Open the **QA Checks** page: every card must equal the value printed in its label (they come from `06_Code/analysis.py`). The league value index must be 1.000.
7. File > Save as .pbix if you need a single file to hand in.

If Desktop reports a schema or TMDL error, note the file named in the message: the project is plain text, so it can be fixed in a text editor (see `NaiviSense_Outcome_Value.Report/definition` and `.SemanticModel/definition`).
Regenerate everything with `python3 ../06_Code/build_pbip.py`.

Mac users: Power BI Desktop is Windows-only. Use a Windows VM, or upload the CSVs to the Power BI Service and rebuild with `DAX_Measures.md`.
""")
    n = sum(len(fs) for _, _, fs in os.walk(OUT))
    print('generated', n, 'files in', OUT, '| measures', len(MEASURES))
