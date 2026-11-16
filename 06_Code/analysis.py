"""Independent re-computation of every headline number (stdlib only).

Run:  python3 analysis.py            -> prints a summary and writes results.json
The Power BI DAX measures must reproduce these numbers (see 02_PowerBI/DAX_Measures.md).
"""
import csv, json, os, statistics as st
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, '..', '01_Data', 'processed')
rd = lambda n: list(csv.DictReader(open(os.path.join(P, n + '.csv'))))
f = lambda x: float(x) if x not in ('', None) else None

child = {r['child_id']: r for r in rd('dim_child')}
agg = rd('agg_child_summary')
ct = rd('fact_child_therapist')
ther = {r['therapist_id']: r for r in rd('dim_therapist')}
alerts = rd('fact_alert')
pays = rd('fact_payment')
dom = rd('fact_assessment_domain')
sess = rd('fact_session')
month = rd('agg_monthly_center')

R = {}
n = len(agg)
R['students'] = n
R['therapists'] = len(ther)
R['sessions_past'] = sum(int(r['sessions_past']) for r in agg)
R['sessions_attended'] = sum(int(r['sessions_attended']) for r in agg)
R['attendance_rate'] = round(R['sessions_attended'] / R['sessions_past'], 4)
R['billed_inr'] = sum(f(r['billed_inr']) for r in agg)
R['collected_inr'] = sum(f(r['collected_inr']) for r in agg)
R['outstanding_inr'] = sum(f(r['outstanding_inr']) for r in agg)
R['collection_rate'] = round(R['collected_inr'] / R['billed_inr'], 4)
R['avg_improvement_pts'] = round(st.mean(f(r['improvement_pts']) for r in agg), 2)
R['children_improved_pct'] = round(sum(f(r['improvement_pts']) > 0 for r in agg) / n, 4)

# ---------- Outcome Value Index ----------
TP = sum(f(r['progress_points']) for r in agg)
TF = sum(f(r['billed_inr']) for r in agg)
for r in agg:
    r['_pp'] = f(r['progress_points']); r['_fee'] = f(r['billed_inr'])
    r['_vi'] = (r['_pp'] / TP) / (r['_fee'] / TF) if r['_fee'] else None
R['total_progress_points'] = round(TP, 1)
R['league_vi_check'] = round(sum(r['_pp'] for r in agg) / TP / (sum(r['_fee'] for r in agg) / TF), 6)
R['median_fee'] = st.median(r['_fee'] for r in agg)
R['median_pp'] = st.median(r['_pp'] for r in agg)


def quad(r):
    hi_fee = r['_fee'] >= R['median_fee']; hi_pp = r['_pp'] >= R['median_pp']
    return {(True, True): 'Thriving', (False, True): 'Efficient', (True, False): 'Under-served', (False, False): 'At-risk'}[(hi_fee, hi_pp)]


for r in agg:
    r['_q'] = quad(r)
R['quadrants'] = {k: sum(1 for r in agg if r['_q'] == k) for k in ['Thriving', 'Efficient', 'Under-served', 'At-risk']}


def vi_group(rows, key):
    g = defaultdict(lambda: [0, 0, 0])
    for r in rows:
        k = key(r); g[k][0] += r['_pp']; g[k][1] += r['_fee']; g[k][2] += 1
    return {k: {'children': v[2], 'fees': round(v[1]), 'progress_pts': round(v[0], 1), 'value_index': round((v[0] / TP) / (v[1] / TF), 2)} for k, v in sorted(g.items())}


for r in agg:
    c = child[r['child_id']]; r.update({'_dx': c['primary_diagnosis'], '_sev': c['severity'], '_inv': c['parent_involvement'], '_age': c['age_band'], '_ntype': c['therapy_type_count']})
R['vi_by_diagnosis'] = vi_group(agg, lambda r: r['_dx'])
R['vi_by_severity'] = vi_group(agg, lambda r: r['_sev'])
R['vi_by_involvement'] = vi_group(agg, lambda r: r['_inv'])
R['vi_by_age_band'] = vi_group(agg, lambda r: r['_age'])
R['vi_by_therapy_count'] = vi_group(agg, lambda r: r['_ntype'])


# monthly fee = subscription billed / number of subscription invoices
for r in agg:
    r['_mfee'] = f(r['monthly_fee_inr'])


def bracket(m):
    return '1 Under 12k' if m < 12000 else '2 12k-15k' if m < 15000 else '3 15k and above'


R['vi_by_monthly_fee_tier'] = vi_group(agg, lambda r: bracket(r['_mfee']))
R['monthly_fee_tier_detail'] = {k: {'avg_attendance': round(st.mean(f(r['attendance_rate']) for r in agg if bracket(r['_mfee']) == k), 3),
                                    'avg_improvement_pts': round(st.mean(f(r['improvement_pts']) for r in agg if bracket(r['_mfee']) == k), 1)}
                                for k in sorted({bracket(r['_mfee']) for r in agg})}
R['corr_monthly_fee_vs_improvement'] = round(st.correlation([r['_mfee'] for r in agg], [f(r['improvement_pts']) for r in agg]), 3)
R['corr_value_index_vs_attendance'] = round(st.correlation([r['_vi'] for r in agg], [f(r['attendance_rate']) for r in agg]), 3)

# therapist / therapy type (attributed by attended-session share)
for key, name in (('therapist_id', 'vi_by_therapist'), ('therapy_type', 'vi_by_therapy_type')):
    g = defaultdict(lambda: [0, 0, 0])
    for r in ct:
        k = ther[r[key]]['therapist_name'] if key == 'therapist_id' else r[key]
        g[k][0] += f(r['attributed_progress_points']); g[k][1] += f(r['attributed_fees_inr']); g[k][2] += int(r['sessions_attended'])
    R[name] = {k: {'sessions': v[2], 'fees': round(v[1]), 'progress_pts': round(v[0], 1), 'value_index': round((v[0] / TP) / (v[1] / TF), 2)} for k, v in sorted(g.items())}

# ---------- drivers ----------
att = [f(r['attendance_rate']) for r in agg]
R['corr_attendance_vs_improvement'] = round(st.correlation(att, [f(r['improvement_pts']) for r in agg]), 3)
R['corr_attendance_vs_progress_points'] = round(st.correlation(att, [r['_pp'] for r in agg]), 3)
R['corr_home_tasks_vs_improvement'] = round(st.correlation([f(r['home_tasks_per_week']) for r in agg], [f(r['improvement_pts']) for r in agg]), 3)
R['corr_total_fees_vs_progress_points'] = round(st.correlation([r['_fee'] for r in agg], [r['_pp'] for r in agg]), 3)
inv = {'low': 1, 'medium': 2, 'high': 3}
R['corr_involvement_vs_improvement'] = round(st.correlation([inv[r['_inv']] for r in agg], [f(r['improvement_pts']) for r in agg]), 3)
R['by_involvement'] = {k: {'children': sum(r['_inv'] == k for r in agg),
                          'attendance': round(st.mean(f(r['attendance_rate']) for r in agg if r['_inv'] == k), 3),
                          'improvement_pts': round(st.mean(f(r['improvement_pts']) for r in agg if r['_inv'] == k), 1),
                          'home_tasks_per_week': round(st.mean(f(r['home_tasks_per_week']) for r in agg if r['_inv'] == k), 2),
                          'collection_rate': round(sum(f(r['collected_inr']) for r in agg if r['_inv'] == k) / sum(f(r['billed_inr']) for r in agg if r['_inv'] == k), 3)}
                       for k in ['low', 'medium', 'high']}

# ---------- domains ----------
dd = defaultdict(lambda: {0: [], 'last': {}})
by_child_dom = defaultdict(list)
for r in dom:
    by_child_dom[(r['child_id'], r['domain'])].append((int(r['seq']), f(r['score']), r['domain_group']))
gain = defaultdict(list); grp = {}
for (c, d), v in by_child_dom.items():
    v.sort(); gain[d].append(v[-1][1] - v[0][1]); grp[d] = v[0][2]
R['domain_gain'] = {d: {'group': grp[d], 'avg_gain_pts': round(st.mean(g), 1)} for d, g in sorted(gain.items(), key=lambda x: -st.mean(x[1]))}

# ---------- alerts ----------
R['alerts_total'] = len(alerts)
R['alerts_open'] = sum(int(a['is_open']) for a in alerts)
sev = defaultdict(list); sevres = defaultdict(list)
for a in alerts:
    sev[a['severity']].append(f(a['hours_to_acknowledge'])); sevres[a['severity']].append(f(a['hours_to_resolve']))
R['alert_sla'] = {k: {'alerts': len(sev[k]), 'avg_hrs_ack': round(st.mean(x for x in sev[k] if x is not None), 1), 'avg_hrs_resolve': round(st.mean(x for x in sevres[k] if x is not None), 1),
                      'ack_within_4h_pct': round(sum(1 for x in sev[k] if x is not None and x <= 4) / len([x for x in sev[k] if x is not None]), 3)} for k in ['high', 'medium', 'low']}
R['alerts_by_type'] = dict(sorted(((t, sum(1 for a in alerts if a['alert_type'] == t)) for t in {a['alert_type'] for a in alerts}), key=lambda x: -x[1]))
R['alerts_per_child_by_severity'] = {k: round(sum(int(r['alerts_total']) for r in agg if r['_sev'] == k) / sum(1 for r in agg if r['_sev'] == k), 2) for k in ['mild', 'moderate', 'severe']}

# ---------- revenue ----------
pst = defaultdict(lambda: [0, 0.0])
for p in pays:
    pst[p['status']][0] += 1; pst[p['status']][1] += f(p['amount_inr'])
R['payments_by_status'] = {k: {'count': v[0], 'inr': v[1]} for k, v in pst.items()}
R['failed_payments'] = pst['failed'][0]
R['top_outstanding'] = sorted(({'child': r['child_code'], 'outstanding_inr': f(r['outstanding_inr'])} for r in agg), key=lambda x: -x['outstanding_inr'])[:5]

# ---------- at risk ----------
R['churn_risk_children'] = sum(int(r['churn_risk']) for r in agg)
R['red_risk_children'] = sum(r['latest_risk'] == 'red' for r in agg)
R['risk_improved_children'] = sum(int(r['risk_improved']) for r in agg)
R['engagement_segments'] = {k: sum(r['engagement_segment'] == k for r in agg) for k in ['High', 'Medium', 'Low']}
top = sorted(agg, key=lambda r: -r['_vi'])
R['top_efficient'] = [{'child': r['child_code'], 'fees': r['_fee'], 'pp': r['_pp'], 'vi': round(r['_vi'], 2)} for r in top[:5]]
R['lowest_value'] = [{'child': r['child_code'], 'fees': r['_fee'], 'pp': r['_pp'], 'vi': round(r['_vi'], 2)} for r in top[-5:]]
R['monthly'] = [{k: m[k] for k in ('month_start', 'sessions_scheduled', 'attendance_rate', 'revenue_billed_inr', 'revenue_collected_inr', 'avg_session_score')} for m in month]
R['sessions_by_mode'] = {m: round(sum(1 for s in sess if s['mode'] == m and s['is_attended'] == '1') / max(1, sum(1 for s in sess if s['mode'] == m and s['is_past'] == '1')), 3) for m in ('online', 'offline')}

json.dump(R, open(os.path.join(HERE, 'results.json'), 'w'), indent=2)
print(json.dumps({k: R[k] for k in ['students', 'attendance_rate', 'collection_rate', 'avg_improvement_pts', 'league_vi_check', 'quadrants', 'vi_by_monthly_fee_tier', 'vi_by_therapy_type', 'vi_by_involvement', 'corr_attendance_vs_improvement', 'corr_total_fees_vs_progress_points', 'corr_monthly_fee_vs_improvement', 'corr_value_index_vs_attendance', 'monthly_fee_tier_detail', 'alert_sla']}, indent=1))
