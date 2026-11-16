"""Renders report figures from the processed CSVs (needs matplotlib). Output: ../03_Report/figures/*.png"""
import csv, json, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, '..', '01_Data', 'processed')
OUT = os.path.join(HERE, '..', '03_Report', 'figures')
os.makedirs(OUT, exist_ok=True)
R = json.load(open(os.path.join(HERE, 'results.json')))
rd = lambda n: list(csv.DictReader(open(os.path.join(P, n + '.csv'))))
f = float
INK, MUTED, GRID, ACC = '#1F1D1A', '#6E6A62', '#ECE8DF', '#2F8F83'
COL = {'Thriving': '#5B7DB1', 'Efficient': '#3BA55C', 'Under-served': '#E5484D', 'At-risk': '#8C8C8C'}
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.edgecolor': GRID, 'axes.labelcolor': MUTED, 'xtick.color': MUTED, 'ytick.color': MUTED,
                     'axes.spines.top': False, 'axes.spines.right': False, 'axes.grid': True, 'grid.color': GRID, 'axes.axisbelow': True})
save = lambda fig, n: (fig.savefig(os.path.join(OUT, n), dpi=170, bbox_inches='tight', facecolor='white'), plt.close(fig))

agg = rd('agg_child_summary')
dim = {r['child_id']: r for r in rd('dim_child')}
TF = sum(f(r['billed_inr']) for r in agg); TP = sum(f(r['progress_points']) for r in agg)
medf = sorted(f(r['billed_inr']) for r in agg); medp = sorted(f(r['progress_points']) for r in agg)
mf = (medf[24] + medf[25]) / 2; mp = (medp[24] + medp[25]) / 2


def grp(r):
    hf, hp = f(r['billed_inr']) >= mf, f(r['progress_points']) >= mp
    return 'Thriving' if hf and hp else 'Efficient' if hp else 'Under-served' if hf else 'At-risk'


# 1 value map
fig, ax = plt.subplots(figsize=(7.2, 4.4))
for g in COL:
    pts = [r for r in agg if grp(r) == g]
    ax.scatter([f(r['billed_inr']) / 1000 for r in pts], [f(r['progress_points']) for r in pts], s=[20 + f(r['sessions_attended']) / 3 for r in pts], c=COL[g], alpha=.85, label=f'{g} ({len(pts)})', edgecolor='white', linewidth=.6)
ax.axvline(mf / 1000, color=INK, ls='--', lw=.8, alpha=.5); ax.axhline(mp, color=INK, ls='--', lw=.8, alpha=.5)
ax.set_xlabel('Fees paid (₹ thousand)'); ax.set_ylabel('Progress points'); ax.legend(frameon=False, loc='upper left', fontsize=8)
ax.set_title('Value map: each dot is one child (dashed = median fee and median progress)', loc='left', color=INK, fontsize=10)
save(fig, 'fig_valuemap.png')

# 2 therapist VI
t = sorted(R['vi_by_therapist'].items(), key=lambda kv: -kv[1]['value_index'])
fig, ax = plt.subplots(figsize=(7.2, 3.6))
ax.bar([k for k, _ in t], [v['value_index'] for _, v in t], color=[ACC if v['value_index'] >= 1 else '#E5484D' for _, v in t])
ax.axhline(1, color=INK, ls='--', lw=.9); ax.text(len(t) - .5, 1.01, 'fair value 1.00', ha='right', fontsize=8, color=INK)
for i, (_, v) in enumerate(t): ax.text(i, v['value_index'] + .015, f"{v['value_index']:.2f}", ha='center', fontsize=8, color=INK)
ax.set_ylabel('Therapist value index'); plt.setp(ax.get_xticklabels(), rotation=25, ha='right'); ax.set_title('Value index by therapist', loc='left', color=INK, fontsize=10)
save(fig, 'fig_therapist.png')

# 3 drivers
fig, axs = plt.subplots(1, 2, figsize=(9.2, 3.8))
x = [f(r['attendance_rate']) for r in agg]; y = [f(r['improvement_pts']) for r in agg]
cmap = {'low': '#E5484D', 'medium': '#F2B84B', 'high': '#3BA55C'}
for k in cmap:
    pts = [r for r in agg if dim[r['child_id']]['parent_involvement'] == k]
    axs[0].scatter([f(r['attendance_rate']) for r in pts], [f(r['improvement_pts']) for r in pts], c=cmap[k], s=28, label=k, edgecolor='white', linewidth=.5)
n = len(x); mx, my = sum(x) / n, sum(y) / n; b = sum((a - mx) * (c - my) for a, c in zip(x, y)) / sum((a - mx) ** 2 for a in x)
xs = [min(x), max(x)]; axs[0].plot(xs, [my + b * (v - mx) for v in xs], color=INK, ls='--', lw=1)
axs[0].set_xlabel('Attendance rate'); axs[0].set_ylabel('Improvement (assessment pts)'); axs[0].legend(title='Parent involvement', frameon=False, fontsize=8)
axs[0].set_title(f'Attendance vs improvement (r = {R["corr_attendance_vs_improvement"]:+.2f})', loc='left', color=INK, fontsize=10)
vi = R['vi_by_involvement']; ks = ['low', 'medium', 'high']
axs[1].bar(ks, [vi[k]['value_index'] for k in ks], color=[cmap[k] for k in ks]); axs[1].axhline(1, color=INK, ls='--', lw=.9)
for i, k in enumerate(ks): axs[1].text(i, vi[k]['value_index'] + .02, f"{vi[k]['value_index']:.2f}", ha='center', fontsize=9)
axs[1].set_ylabel('Outcome value index'); axs[1].set_title('Value index by parent involvement', loc='left', color=INK, fontsize=10)
fig.tight_layout(); save(fig, 'fig_drivers.png')

# 4 domains
d = list(R['domain_gain'].items())[::-1]
fig, ax = plt.subplots(figsize=(7.2, 4.4))
gc = {'Communication': '#5B7DB1', 'Motor & Daily Living': '#3BA55C', 'Cognition & Learning': '#F2B84B', 'Behaviour & Regulation': '#7B61C9'}
ax.barh([k.replace('_', ' ') for k, _ in d], [v['avg_gain_pts'] for _, v in d], color=[gc[v['group']] for _, v in d])
for i, (_, v) in enumerate(d): ax.text(v['avg_gain_pts'] + .1, i, f"{v['avg_gain_pts']:.1f}", va='center', fontsize=8)
ax.set_xlabel('Average gain (points, initial → latest assessment)'); ax.set_title('Which domains improve fastest', loc='left', color=INK, fontsize=10)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=c, label=g) for g, c in gc.items()], frameon=False, fontsize=8, loc='lower right'); save(fig, 'fig_domains.png')

# 5 alerts
s = R['alert_sla']; sv = ['high', 'medium', 'low']
fig, axs = plt.subplots(1, 2, figsize=(8, 3.3))
axs[0].bar(sv, [s[k]['avg_hrs_ack'] for k in sv], color=['#E5484D', '#F2B84B', '#8C8C8C']); axs[0].set_ylabel('Hours'); axs[0].set_title('Average hours to acknowledge', loc='left', color=INK, fontsize=10)
axs[1].bar(sv, [s[k]['avg_hrs_resolve'] for k in sv], color=['#E5484D', '#F2B84B', '#8C8C8C']); axs[1].set_title('Average hours to resolve', loc='left', color=INK, fontsize=10)
for a, key in zip(axs, ['avg_hrs_ack', 'avg_hrs_resolve']):
    for i, k in enumerate(sv): a.text(i, s[k][key] + 1, f'{s[k][key]:.1f}', ha='center', fontsize=8)
fig.tight_layout(); save(fig, 'fig_alerts.png')

# 6 revenue
m = R['monthly']
fig, ax = plt.subplots(figsize=(7.2, 3.5))
xs = range(len(m)); ax.bar([i - .2 for i in xs], [float(r['revenue_billed_inr']) / 1e5 for r in m], .4, label='Billed', color='#C9C5BC')
ax.bar([i + .2 for i in xs], [float(r['revenue_collected_inr']) / 1e5 for r in m], .4, label='Collected', color=ACC)
ax.set_xticks(list(xs)); ax.set_xticklabels([r['month_start'][:7] for r in m]); ax.set_ylabel('₹ lakh'); ax.legend(frameon=False)
ax.set_title(f'Billed vs collected by month (overall collection {R["collection_rate"]:.0%})', loc='left', color=INK, fontsize=10); save(fig, 'fig_revenue.png')


# 7 star schema + 8 architecture
def box(ax, x, y, w, h, txt, fc, tc='white', fs=8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.02,rounding_size=0.08', fc=fc, ec='none')); ax.text(x + w / 2, y + h / 2, txt, ha='center', va='center', color=tc, fontsize=fs, fontweight='bold')


fig, ax = plt.subplots(figsize=(8.4, 5)); ax.set_xlim(0, 12); ax.set_ylim(0, 8); ax.axis('off'); ax.grid(False)
dims = {'dim_date': (5, 3.4), 'dim_child': (5, 5.6), 'dim_therapist': (9.2, 5.6)}
for n_, (x_, y_) in dims.items(): box(ax, x_, y_, 2.4, .8, n_, '#2F8F83')
box(ax, 5, 1.2, 2.4, .8, 'dim_week', '#2F8F83'); box(ax, 9.2, 3.4, 2.4, .8, 'agg_child_summary', '#8C8C8C')
facts = [('fact_session', 0.2, 6.9), ('fact_assessment', 0.2, 5.6), ('fact_assessment_domain', 0.2, 4.3), ('fact_alert', 0.2, 3.0), ('fact_payment', 0.2, 1.7), ('fact_goal', 0.2, 0.4),
         ('fact_child_therapist', 9.2, 7.0), ('fact_home_engagement', 9.2, 0.4)]
for n_, x_, y_ in facts: box(ax, x_, y_, 2.6 if x_ < 9 else 2.6, .8, n_, '#5B7DB1', fs=7)
for _, x_, y_ in facts[:6]: ax.annotate('', xy=(5, 6.0), xytext=(2.8, y_ + .4), arrowprops=dict(arrowstyle='->', color='#A8A396', lw=.8))
ax.annotate('', xy=(10.4, 6.4), xytext=(10.4, 7.0), arrowprops=dict(arrowstyle='->', color='#A8A396', lw=.8)); ax.annotate('', xy=(7.4, 6.0), xytext=(9.2, 7.2), arrowprops=dict(arrowstyle='->', color='#A8A396', lw=.8))
ax.annotate('', xy=(7.4, 1.5), xytext=(9.2, 0.8), arrowprops=dict(arrowstyle='->', color='#A8A396', lw=.8)); ax.annotate('', xy=(9.4, 4.2), xytext=(9.8, 3.4), arrowprops=dict(arrowstyle='-', color='white', lw=0)); ax.annotate('', xy=(8.6, 4.9), xytext=(10.0, 5.6), arrowprops=dict(arrowstyle='-', color='white', lw=0)); ax.annotate('', xy=(6.2, 3.4), xytext=(6.2, 2.0), arrowprops=dict(arrowstyle='->', color='#A8A396', lw=.8))
ax.annotate('', xy=(7.4, 5.9), xytext=(9.2, 3.9), arrowprops=dict(arrowstyle='<->', color='#8C8C8C', lw=.8, ls='--'))
ax.text(0.2, 7.95 - 0.1, '', fontsize=1); ax.text(3.1, -0.45, 'All facts also join dim_date through their date column; fact_session and fact_child_therapist join dim_therapist;\nfact_home_engagement joins dim_child as well as dim_week. All relationships are many-to-one (dimension filters fact).', fontsize=7, color=MUTED, clip_on=False)
ax.set_title('Star schema (teal = dimensions, blue = facts, grey = child summary)', loc='left', color=INK, fontsize=10); save(fig, 'fig_schema.png')

fig, ax = plt.subplots(figsize=(9, 2.4)); ax.set_xlim(0, 12); ax.set_ylim(0, 3); ax.axis('off'); ax.grid(False)
steps = [('Flutter app +\nExpress API', '#8C8C8C'), ('MongoDB Atlas\nraw collections', '#2F8F83'), ('process.ts\nstar schema', '#5B7DB1'), ('proc_* collections\n+ CSV export', '#2F8F83'), ('Power BI\nPBIP model', '#F2B84B')]
for i, (tx, c) in enumerate(steps):
    box(ax, .1 + i * 2.4, 1, 2.0, 1.1, tx, c, fs=8, tc='white' if c != '#F2B84B' else INK)
    if i < 4: ax.annotate('', xy=(2.5 + i * 2.4, 1.55), xytext=(2.1 + i * 2.4, 1.55), arrowprops=dict(arrowstyle='->', color=INK, lw=1.2))
ax.text(.1, .35, 'Raw (as stored by the app) → Processed (analysis-ready) → Report', color=MUTED, fontsize=8); save(fig, 'fig_architecture.png')
print('figures:', sorted(os.listdir(OUT)))
