/**
 * RAW -> PROCESSED. Builds a Power-BI-friendly star schema from raw rows.
 * Keys are strings (ObjectId hex) so they join cleanly in Power BI.
 */
import { DOMAINS, DATA_END, Row, RawData } from './generate';

const s = (v: unknown) => (v == null ? '' : String(v));
const day = (d: unknown) => (d ? new Date(d as Date).toISOString().slice(0, 10) : null);
const mean = (a: number[]) => (a.length ? a.reduce((x, y) => x + y, 0) / a.length : 0);
const r1 = (n: number) => Math.round(n * 10) / 10;
const r2 = (n: number) => Math.round(n * 100) / 100;
const monthStart = (d: Date) => new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), 1)).toISOString().slice(0, 10);
const weekStart = (d: Date) => {
  const x = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()));
  x.setUTCDate(x.getUTCDate() - ((x.getUTCDay() + 6) % 7));
  return x.toISOString().slice(0, 10);
};

const DOMAIN_GROUP: Record<string, string> = {
  attention: 'Behaviour & Regulation', behavioral: 'Behaviour & Regulation', emotional_regulation: 'Behaviour & Regulation',
  social_communication: 'Communication', receptive_language: 'Communication', expressive_language: 'Communication', speech_production: 'Communication',
  imitation: 'Cognition & Learning', visual_perception: 'Cognition & Learning', cognitive: 'Cognition & Learning', academics: 'Cognition & Learning',
  fine_motor: 'Motor & Daily Living', gross_motor: 'Motor & Daily Living', sensory: 'Motor & Daily Living', adl: 'Motor & Daily Living',
};

export type Processed = Record<string, Row[]>;

export function process(raw: RawData): Processed {
  const attBySession = new Map(raw.attendances.map((a) => [s(a.session_id), a]));

  // dim_date
  const dim_date: Row[] = [];
  for (let d = new Date(Date.UTC(2026, 3, 1)); d <= new Date(Date.UTC(2026, 11, 31)); d = new Date(d.getTime() + 86400000)) {
    const dow = (d.getUTCDay() + 6) % 7;
    dim_date.push({
      date: d.toISOString().slice(0, 10), year: d.getUTCFullYear(), month_num: d.getUTCMonth() + 1,
      month_name: d.toLocaleString('en-US', { month: 'long', timeZone: 'UTC' }), month_start: monthStart(d),
      week_start: weekStart(d), day_of_week: dow + 1, day_name: d.toLocaleString('en-US', { weekday: 'long', timeZone: 'UTC' }),
      is_weekend: dow >= 5, is_future: d > DATA_END,
    });
  }

  // dim_therapist
  const caseload = new Map<string, Set<string>>();
  for (const c of raw.children) for (const t of c.therapists as Row[]) {
    const k = s(t.therapist_id); (caseload.get(k) ?? caseload.set(k, new Set()).get(k)!).add(s(c._id));
  }
  const specialty = new Map<string, string>();
  for (const x of raw.sessions) specialty.set(s(x.therapist_id), s(x.type));
  const dim_therapist: Row[] = raw.users.filter((u) => u.role === 'therapist').map((u) => ({
    therapist_id: s(u._id), therapist_name: u.name, specialty: specialty.get(s(u._id)) ?? '', caseload_children: caseload.get(s(u._id))?.size ?? 0,
  }));

  // fact_session (one row per scheduled session incl. future)
  const fact_session: Row[] = raw.sessions.map((x) => {
    const n = (x.notes ?? {}) as Record<string, number | string | boolean>;
    const sc = ['attention_score', 'communication_score', 'motor_score', 'behavior_score'].map((k) => n[k] as number).filter((v) => typeof v === 'number');
    const att = attBySession.get(s(x._id));
    const at = new Date(x.scheduled_at as Date);
    return {
      session_id: s(x._id), child_id: s(x.child_id), therapist_id: s(x.therapist_id), date: day(at), month_start: monthStart(at),
      week_start: weekStart(at), start_hour: at.getUTCHours(), therapy_type: x.type, mode: x.mode, duration_min: x.duration_min,
      session_status: x.status, attendance_status: att ? att.status : (x.status === 'scheduled' ? 'upcoming' : ''),
      is_attended: att ? (att.status !== 'absent' ? 1 : 0) : null, is_past: at <= DATA_END ? 1 : 0,
      mood: n.mood ?? null, attention_score: n.attention_score ?? null, communication_score: n.communication_score ?? null,
      motor_score: n.motor_score ?? null, behavior_score: n.behavior_score ?? null, avg_session_score: sc.length ? r2(mean(sc)) : null,
      tantrum_observed: n.tantrums_observed ? 1 : n.mood ? 0 : null, follow_up_required: n.follow_up_required ? 1 : n.mood ? 0 : null,
    };
  });

  // fact_assessment (wide) + fact_assessment_domain (long)
  const fact_assessment: Row[] = [];
  const fact_assessment_domain: Row[] = [];
  const lastSeq = new Map<string, number>();
  for (const h of raw.assessment_history) lastSeq.set(s(h.child_id), Math.max(lastSeq.get(s(h.child_id)) ?? 0, h.seq as number));
  for (const h of raw.assessment_history) {
    const ds = h.domain_scores as Record<string, number>;
    const base = { child_id: s(h.child_id), assessment_date: day(h.date), month_start: monthStart(new Date(h.date as Date)), seq: h.seq, assessment_type: h.type };
    fact_assessment.push({ ...base, overall_score_pct: h.overall_score_pct, risk_level: h.risk_level, developmental_quotient: h.developmental_quotient, ...ds });
    for (const d of DOMAINS) fact_assessment_domain.push({ ...base, domain: d, domain_group: DOMAIN_GROUP[d], score: ds[d], is_initial: h.seq === 0 ? 1 : 0, is_latest: h.seq === lastSeq.get(s(h.child_id)) ? 1 : 0 });
  }

  // fact_alert
  const fact_alert: Row[] = raw.alerts.map((a) => {
    const c = new Date(a.created_at as Date);
    const ack = a.acknowledged_at ? new Date(a.acknowledged_at as Date) : null;
    const res = a.resolved_at ? new Date(a.resolved_at as Date) : null;
    return {
      alert_id: s(a._id), child_id: s(a.child_id), created_date: day(c), month_start: monthStart(c), alert_type: a.type, category: a.category,
      severity: a.severity, source: a.source, status: a.status, is_open: a.status === 'open' ? 1 : 0,
      hours_to_acknowledge: ack ? r1((ack.getTime() - c.getTime()) / 3600000) : null,
      hours_to_resolve: res ? r1((res.getTime() - c.getTime()) / 3600000) : null,
    };
  });

  // fact_payment
  const fact_payment: Row[] = raw.payments.map((p) => {
    const c = new Date(p.created_at as Date);
    return {
      payment_id: s(p._id), child_id: p.child_id, parent_user_id: p.parent_id, billing_date: day(c), month_start: monthStart(c),
      payment_type: p.type, status: p.status, amount_inr: (p.amount_paise as number) / 100,
      paid_amount_inr: p.status === 'paid' ? (p.amount_paise as number) / 100 : 0,
      outstanding_inr: p.status === 'pending' || p.status === 'failed' ? (p.amount_paise as number) / 100 : 0,
      days_to_pay: p.paid_at ? Math.round((new Date(p.paid_at as Date).getTime() - c.getTime()) / 86400000) : null,
    };
  });

  // fact_goal
  const fact_goal: Row[] = raw.goals.map((g) => ({
    goal_id: s(g._id), child_id: s(g.child_id), title: g.title, status: g.status, priority: g.priority,
    created_date: day(g.created_at), target_date: day(g.target_date), is_completed: g.status === 'completed' ? 1 : 0,
  }));

  // fact_home_engagement_weekly
  const wk = new Map<string, Row>();
  const bump = (child: string, week: string, f: string, by = 1) => {
    const k = `${child}|${week}`;
    const r = wk.get(k) ?? { child_id: child, week_start: week, meals_logged: 0, home_tasks_logged: 0, home_tasks_approved: 0, sessions_scheduled: 0, sessions_attended: 0 };
    r[f] = (r[f] as number) + by; wk.set(k, r);
  };
  for (const m of raw.meal_logs) bump(s(m.child_id), weekStart(new Date(m.logged_at as Date)), 'meals_logged');
  for (const t of raw.home_task_logs) {
    const w = weekStart(new Date(t.logged_at as Date));
    bump(s(t.child_id), w, 'home_tasks_logged'); if (t.status === 'approved') bump(s(t.child_id), w, 'home_tasks_approved');
  }
  for (const x of fact_session) if (x.is_past) {
    bump(s(x.child_id), s(x.week_start), 'sessions_scheduled'); if (x.is_attended) bump(s(x.child_id), s(x.week_start), 'sessions_attended');
  }
  const fact_home_engagement_weekly = [...wk.values()];

  // dim_child + agg_child_summary
  const byChild = <T extends Row>(rows: T[], key = 'child_id') => {
    const m = new Map<string, T[]>(); for (const r of rows) { const k = s(r[key]); (m.get(k) ?? m.set(k, []).get(k)!).push(r); } return m;
  };
  const sessByChild = byChild(fact_session), alertByChild = byChild(fact_alert), payByChild = byChild(fact_payment);
  const assessByChild = byChild(fact_assessment), goalByChild = byChild(fact_goal), engByChild = byChild(fact_home_engagement_weekly);

  const dim_child: Row[] = [];
  const agg_child_summary: Row[] = [];
  for (const [ci, c] of raw.children.entries()) {
    const id = s(c._id);
    const code = `C${String(ci + 1).padStart(3, '0')}`; // processed layer identifies children by code, not name
    const dob = new Date(c.dob as Date);
    const age = Math.floor((DATA_END.getTime() - dob.getTime()) / (365.25 * 86400000));
    const enrolled = new Date(c.enrolled_at as Date);
    const hc = c.home_context as Record<string, unknown>;
    const med = c.medical as Record<string, unknown>;
    const ths = c.therapists as Row[];
    dim_child.push({
      child_id: id, child_code: code, gender: c.gender, age_years: age, age_band: age <= 4 ? '3-4' : age <= 7 ? '5-7' : age <= 10 ? '8-10' : '11-12',
      primary_diagnosis: (c.diagnosis as string[])[0], diagnosis_count: (c.diagnosis as string[]).length, severity: c.severity,
      enrollment_date: day(enrolled), enrollment_month: monthStart(enrolled), therapy_types: ths.map((t) => t.therapy_type).join('|'), therapy_type_count: ths.length,
      parent_involvement: hc.parent_involvement, screen_time_hours: hc.screen_time_hours, play_type: hc.play_type,
      birth_history: med.birth_history, milestones_delay: med.milestones_delay ? 1 : 0, parent_user_id: s(c.parent_id),
    });

    const past = (sessByChild.get(id) ?? []).filter((x) => x.is_past === 1);
    const attended = past.filter((x) => x.is_attended === 1).length;
    const att_rate = past.length ? attended / past.length : 0;
    const scores = past.map((x) => x.avg_session_score as number).filter((v) => typeof v === 'number');
    const half = Math.floor(scores.length / 2);
    const ass = (assessByChild.get(id) ?? []).sort((a, b) => (a.seq as number) - (b.seq as number));
    const first = ass[0], last = ass[ass.length - 1];
    const gain = first && last ? (last.overall_score_pct as number) - (first.overall_score_pct as number) : 0;
    const al = alertByChild.get(id) ?? [];
    const pay = (payByChild.get(id) ?? []).filter((p) => p.payment_type === 'subscription');
    const eng = engByChild.get(id) ?? [];
    const tasksPerWeek = eng.length ? mean(eng.map((e) => e.home_tasks_logged as number)) : 0;
    const gl = goalByChild.get(id) ?? [];
    const segment = att_rate >= 0.85 && tasksPerWeek >= 3.5 ? 'High' : att_rate < 0.72 || tasksPerWeek < 2 ? 'Low' : 'Medium';
    const churn_risk = att_rate < 0.7 || (last?.risk_level === 'red' && gain < 3) || pay.filter((p) => p.status === 'failed').length >= 2;
    agg_child_summary.push({
      child_id: id, child_code: code, sessions_past: past.length, sessions_attended: attended, attendance_rate: r2(att_rate),
      avg_session_score: r2(mean(scores)), session_score_first_half: r2(mean(scores.slice(0, half))), session_score_second_half: r2(mean(scores.slice(half))),
      initial_overall_score: first?.overall_score_pct ?? null, latest_overall_score: last?.overall_score_pct ?? null, improvement_pts: r1(gain),
      improvement_pct: first ? r1((gain / (first.overall_score_pct as number)) * 100) : null,
      months_tracked: ass.length - 1, initial_risk: first?.risk_level ?? null, latest_risk: last?.risk_level ?? null,
      risk_improved: first && last && ['red', 'amber', 'green'].indexOf(last.risk_level as string) > ['red', 'amber', 'green'].indexOf(first.risk_level as string) ? 1 : 0,
      alerts_total: al.length, alerts_open: al.filter((a) => a.is_open === 1).length, high_severity_alerts: al.filter((a) => a.severity === 'high').length,
      billed_inr: pay.reduce((x, p) => x + (p.amount_inr as number), 0), collected_inr: pay.reduce((x, p) => x + (p.paid_amount_inr as number), 0),
      outstanding_inr: pay.reduce((x, p) => x + (p.outstanding_inr as number), 0), home_tasks_per_week: r2(tasksPerWeek),
      meals_logged_per_week: r2(eng.length ? mean(eng.map((e) => e.meals_logged as number)) : 0),
      goals_total: gl.length, goals_completed: gl.filter((g) => g.is_completed === 1).length, engagement_segment: segment, churn_risk: churn_risk ? 1 : 0,
      subscription_invoices: pay.length, monthly_fee_inr: pay.length ? Math.round(pay.reduce((x, p) => x + (p.amount_inr as number), 0) / pay.length) : 0,
      // Progress Points = 10 x assessment gain + 20 x session-score gain + 5 x goals completed (floored at 0)
      progress_points: r1(Math.max(0, 10 * gain + 20 * (mean(scores.slice(half)) - mean(scores.slice(0, half))) + 5 * gl.filter((g) => g.is_completed === 1).length)),
    });
  }

  // fact_child_therapist: a child's progress and fees are shared between therapists by attended-session share.
  const att = new Map<string, Map<string, { n: number; type: string }>>();
  for (const x of fact_session) if (x.is_attended === 1) {
    const m = att.get(s(x.child_id)) ?? att.set(s(x.child_id), new Map()).get(s(x.child_id))!;
    const e = m.get(s(x.therapist_id)) ?? { n: 0, type: s(x.therapy_type) }; e.n++; m.set(s(x.therapist_id), e);
  }
  const fact_child_therapist: Row[] = [];
  for (const row of agg_child_summary) {
    const m = att.get(s(row.child_id)); if (!m) continue;
    const total = [...m.values()].reduce((x, e) => x + e.n, 0);
    for (const [tid, e] of m) {
      const share = e.n / total;
      fact_child_therapist.push({
        child_id: row.child_id, therapist_id: tid, therapy_type: e.type, sessions_attended: e.n, session_share: r2(share),
        attributed_progress_points: r1((row.progress_points as number) * share), attributed_fees_inr: Math.round((row.billed_inr as number) * share),
      });
    }
  }

  // agg_monthly_center
  const months = new Set<string>(fact_session.map((x) => s(x.month_start)));
  const agg_monthly_center: Row[] = [...months].sort().map((m) => {
    const ss = fact_session.filter((x) => x.month_start === m && x.is_past === 1);
    const att = ss.filter((x) => x.is_attended === 1);
    const sc = att.map((x) => x.avg_session_score as number).filter((v) => typeof v === 'number');
    const pm = fact_payment.filter((x) => x.month_start === m);
    const am = fact_assessment.filter((x) => x.month_start === m);
    return {
      month_start: m, sessions_scheduled: ss.length, sessions_attended: att.length, attendance_rate: r2(ss.length ? att.length / ss.length : 0),
      avg_session_score: r2(mean(sc)), active_children: new Set(ss.map((x) => x.child_id)).size, revenue_billed_inr: pm.reduce((x, p) => x + (p.amount_inr as number), 0),
      revenue_collected_inr: pm.reduce((x, p) => x + (p.paid_amount_inr as number), 0), alerts_raised: fact_alert.filter((a) => a.month_start === m).length,
      avg_overall_assessment: r1(mean(am.map((a) => a.overall_score_pct as number))),
    };
  });

  return {
    dim_date, dim_child, dim_therapist, fact_session, fact_assessment, fact_assessment_domain, fact_alert, fact_payment,
    fact_goal, fact_home_engagement_weekly, fact_child_therapist, agg_child_summary, agg_monthly_center,
  };
}
