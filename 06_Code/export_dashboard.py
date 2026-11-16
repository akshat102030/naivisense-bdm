"""Exports the dashboard data (../web/src/data/dashboard.json) from the processed CSVs and results.json (stdlib only).

Run after analysis.py:   python3 export_dashboard.py
The web app imports this one JSON file, so the site build needs no Python and no database.
Children are identified by code (C001-C050) only.
"""
import csv, json, os, statistics as st
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, '..', '01_Data', 'processed')
OUT = os.path.join(HERE, '..', 'web', 'src', 'data', 'dashboard.json')
rd = lambda n: list(csv.DictReader(open(os.path.join(P, n + '.csv'))))
f = float
R = json.load(open(os.path.join(HERE, 'results.json')))

agg = rd('agg_child_summary'); dim = {r['child_id']: r for r in rd('dim_child')}
ther = {r['therapist_id']: r for r in rd('dim_therapist')}; ct = rd('fact_child_therapist')
TF = sum(f(r['billed_inr']) for r in agg); TP = sum(f(r['progress_points']) for r in agg)
fees = sorted(f(r['billed_inr']) for r in agg); pps = sorted(f(r['progress_points']) for r in agg)
mf, mp = st.median(fees), st.median(pps)

children = []
for r in agg:
    d = dim[r['child_id']]; fee, pp = f(r['billed_inr']), f(r['progress_points'])
    group = ('Thriving' if pp >= mp else 'Under-served') if fee >= mf else ('Efficient' if pp >= mp else 'At-risk')
    children.append({
        'code': r['child_code'], 'group': group, 'fees': round(fee), 'progress': round(pp, 1), 'valueIndex': round((pp / TP) / (fee / TF), 2),
        'attendance': round(f(r['attendance_rate']) * 100, 1), 'improvement': f(r['improvement_pts']), 'sessions': int(r['sessions_attended']),
        'initialScore': f(r['initial_overall_score']), 'latestScore': f(r['latest_overall_score']), 'initialRisk': r['initial_risk'], 'latestRisk': r['latest_risk'],
        'alerts': int(r['alerts_total']), 'openAlerts': int(r['alerts_open']), 'outstanding': round(f(r['outstanding_inr'])), 'monthlyFee': int(r['monthly_fee_inr']),
        'homeTasksPerWeek': f(r['home_tasks_per_week']), 'goalsCompleted': int(r['goals_completed']), 'goalsTotal': int(r['goals_total']), 'churnRisk': r['churn_risk'] == '1',
        'diagnosis': d['primary_diagnosis'], 'severity': d['severity'], 'involvement': d['parent_involvement'], 'ageBand': d['age_band'], 'gender': d['gender'], 'ageYears': int(d['age_years']),
        'therapies': d['therapy_types'].split('|'),
    })
children.sort(key=lambda c: c['code'])

# therapist rows with specialty and caseload
spec = {}
for r in ct: spec[r['therapist_id']] = r['therapy_type']
therapists = []
for name, v in R['vi_by_therapist'].items():
    tid = next(k for k, t in ther.items() if t['therapist_name'] == name)
    therapists.append({'name': name, 'specialty': spec.get(tid, ther[tid]['specialty']), 'caseload': int(ther[tid]['caseload_children']), **{k: v[k] for k in ('sessions', 'fees', 'value_index')}, 'progress': v['progress_pts']})
therapists.sort(key=lambda t: -t['value_index'])

def grp(d):
    return [{'label': k, **v} for k, v in d.items()]

pay = R['payments_by_status']
data = {
    'meta': {'students': R['students'], 'therapists': R['therapists'], 'period': 'May–Nov 2026', 'medianFee': mf, 'medianProgress': mp, 'generated': 'sample data'},
    'kpi': {k: R[k] for k in ('students', 'therapists', 'sessions_past', 'sessions_attended', 'attendance_rate', 'billed_inr', 'collected_inr', 'outstanding_inr', 'collection_rate',
                              'avg_improvement_pts', 'churn_risk_children', 'red_risk_children', 'risk_improved_children', 'failed_payments', 'alerts_total', 'alerts_open')},
    'quadrants': R['quadrants'], 'children': children, 'therapists': therapists, 'therapyTypes': grp(R['vi_by_therapy_type']),
    'involvement': [{'label': k, **R['vi_by_involvement'][k], **{kk: R['by_involvement'][k][kk] for kk in ('attendance', 'improvement_pts', 'home_tasks_per_week', 'collection_rate')}} for k in ('low', 'medium', 'high')],
    'bySeverity': grp(R['vi_by_severity']), 'byDiagnosis': grp(R['vi_by_diagnosis']), 'byAgeBand': grp(R['vi_by_age_band']), 'byFeeTier': grp(R['vi_by_monthly_fee_tier']),
    'feeTierDetail': R['monthly_fee_tier_detail'],
    'correlations': {'attendanceVsImprovement': R['corr_attendance_vs_improvement'], 'homeTasksVsImprovement': R['corr_home_tasks_vs_improvement'], 'monthlyFeeVsImprovement': R['corr_monthly_fee_vs_improvement'],
                     'involvementVsImprovement': R['corr_involvement_vs_improvement']},
    'domains': [{'domain': k.replace('_', ' '), 'group': v['group'], 'gain': v['avg_gain_pts']} for k, v in R['domain_gain'].items()],
    'alerts': {'sla': [{'severity': k, **v} for k, v in R['alert_sla'].items()], 'byType': [{'type': k.replace('_', ' '), 'count': v} for k, v in R['alerts_by_type'].items()],
               'perChildBySeverity': R['alerts_per_child_by_severity']},
    'revenue': {'monthly': [{'month': m['month_start'][:7], 'billed': f(m['revenue_billed_inr']), 'collected': f(m['revenue_collected_inr']), 'attendance': f(m['attendance_rate'])} for m in R['monthly']],
                'byStatus': [{'status': k, 'count': v['count'], 'inr': v['inr']} for k, v in pay.items()], 'topOutstanding': R['top_outstanding']},
    'engagement': R['engagement_segments'],
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(data, open(OUT, 'w'), indent=1)
print('wrote', os.path.abspath(OUT), os.path.getsize(OUT), 'bytes;', len(children), 'children')
