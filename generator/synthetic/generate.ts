/**
 * Deterministic sample-data generator for NaiviSense analytics.
 * Pure (no I/O): returns RAW collections shaped like the app's Mongo models,
 * plus an `assessment_history` collection (monthly snapshots) the app model
 * does not keep. Latent traits (responsiveness, parent involvement) drive
 * attendance, home engagement and improvement, so the dashboard has real
 * relationships to discover.
 */
import { ObjectId } from 'bson';

export const SEED = 20261116;
export const DATA_START = new Date('2026-05-04T00:00:00Z'); // Monday
export const DATA_END = new Date('2026-11-15T23:59:59Z'); // "today" for history
export const FUTURE_WEEKS = 2;

export const DOMAINS = [
  'attention', 'behavioral', 'social_communication', 'receptive_language',
  'expressive_language', 'speech_production', 'imitation', 'visual_perception',
  'fine_motor', 'gross_motor', 'sensory', 'adl', 'academics', 'cognitive',
  'emotional_regulation',
] as const;
export type Domain = (typeof DOMAINS)[number];

export const THERAPY_TYPES = ['speech', 'ot', 'behavior', 'special_ed'] as const;
type TherapyType = (typeof THERAPY_TYPES)[number];

// Which assessment domains each therapy type mainly moves.
const TYPE_DOMAINS: Record<TherapyType, Domain[]> = {
  speech: ['receptive_language', 'expressive_language', 'speech_production', 'social_communication'],
  ot: ['fine_motor', 'gross_motor', 'sensory', 'adl', 'visual_perception'],
  behavior: ['behavioral', 'emotional_regulation', 'attention', 'imitation'],
  special_ed: ['academics', 'cognitive', 'attention', 'visual_perception'],
};

function mulberry32(a: number) {
  return () => {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export type Row = Record<string, unknown>;
export interface RawData {
  users: Row[]; parent_profiles: Row[]; children: Row[]; sessions: Row[];
  attendances: Row[]; assessments: Row[]; assessment_history: Row[];
  goals: Row[]; alerts: Row[]; concerns: Row[]; payments: Row[];
  meal_logs: Row[]; home_task_logs: Row[];
}

export function generate(passwordHash: string, studentCount = 50): RawData {
  const rnd = mulberry32(SEED);
  const pick = <T,>(a: readonly T[]): T => a[Math.floor(rnd() * a.length)];
  const between = (lo: number, hi: number) => lo + rnd() * (hi - lo);
  const int = (lo: number, hi: number) => Math.floor(between(lo, hi + 1));
  const clamp = (v: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, v));
  const chance = (p: number) => rnd() < p;
  const weighted = <T,>(items: readonly T[], w: number[]): T => {
    let r = rnd() * w.reduce((s, x) => s + x, 0);
    for (let i = 0; i < items.length; i++) { r -= w[i]; if (r <= 0) return items[i]; }
    return items[items.length - 1];
  };
  // Deterministic ids from a separate stream, so the data stream above is unchanged and re-runs yield identical keys.
  const idRnd = mulberry32(SEED + 1);
  const oid = () => new ObjectId(Array.from({ length: 12 }, () => Math.floor(idRnd() * 256).toString(16).padStart(2, '0')).join(''));
  const addDays = (d: Date, n: number) => new Date(d.getTime() + n * 86400000);
  const withTime = (d: Date, hh: number, mm = 0) => {
    const x = new Date(d); x.setUTCHours(hh, mm, 0, 0); return x;
  };

  const out: RawData = {
    users: [], parent_profiles: [], children: [], sessions: [], attendances: [],
    assessments: [], assessment_history: [], goals: [], alerts: [], concerns: [],
    payments: [], meal_logs: [], home_task_logs: [],
  };
  const tag = { synthetic: true };

  // ---- staff -------------------------------------------------------------
  let phoneSeq = 7000000000;
  const nextPhone = () => `+91${phoneSeq++}`;
  const mkUser = (name: string, role: string, email?: string) => {
    const _id = oid();
    const created_at = addDays(DATA_START, -int(20, 120));
    out.users.push({
      _id, name, role, phone: nextPhone(), email, password_hash: passwordHash,
      is_verified: true, created_at, updated_at: created_at, ...tag,
    });
    return _id;
  };
  const centerId = mkUser('Arjun Sharma', 'center_head', 'center@example.test');
  const therapistNames: Record<TherapyType, string[]> = {
    speech: ['Priya Mehta', 'Kavya Iyer'],
    ot: ['Rohan Verma', 'Neha Bansal'],
    behavior: ['Sneha Kapoor', 'Imran Sheikh'],
    special_ed: ['Amit Joshi', 'Ritu Malhotra'],
  };
  const therapists: { id: ObjectId; name: string; type: TherapyType; skill: number }[] = [];
  for (const t of THERAPY_TYPES) {
    for (const n of therapistNames[t]) {
      therapists.push({ id: mkUser(n, 'therapist'), name: n, type: t, skill: between(0.85, 1.15) });
    }
  }
  mkUser('Dr. Meera Pillai', 'dietician');
  const psychId = mkUser('Dr. Karan Bedi', 'clinical_psychologist');
  void psychId;

  // ---- reference vocab ---------------------------------------------------
  const firstBoys = ['Aarav', 'Vihaan', 'Reyansh', 'Arjun', 'Kabir', 'Ishaan', 'Advik', 'Ayaan', 'Dev', 'Rudra', 'Yash', 'Krish', 'Veer', 'Neil', 'Om', 'Samar', 'Tanay', 'Dhruv'];
  const firstGirls = ['Anaya', 'Myra', 'Diya', 'Aadhya', 'Siya', 'Pari', 'Kiara', 'Riya', 'Ira', 'Navya', 'Tara', 'Zoya', 'Meher', 'Anvi', 'Sara', 'Ahana'];
  const lastNames = ['Sharma', 'Verma', 'Gupta', 'Singh', 'Rao', 'Nair', 'Patel', 'Joshi', 'Kulkarni', 'Reddy', 'Khan', 'Mishra', 'Bose', 'Chopra', 'Tiwari', 'Saxena', 'Yadav', 'Menon'];
  const parentFirst = ['Sunita', 'Vikram', 'Deepa', 'Rajesh', 'Anita', 'Manoj', 'Pooja', 'Sanjay', 'Rekha', 'Alok', 'Shweta', 'Nitin', 'Seema', 'Gaurav', 'Madhu', 'Anil', 'Lata', 'Suresh'];
  const diagnoses = ['Autism Spectrum Disorder', 'ADHD', 'Speech & Language Delay', 'Global Developmental Delay', 'Down Syndrome', 'Cerebral Palsy', 'Sensory Processing Disorder'];
  const diagWeights = [30, 18, 20, 12, 7, 5, 8];
  const concernPool = ['Delayed speech', 'Poor eye contact', 'Frequent tantrums', 'Sensory sensitivity', 'Short attention span', 'Poor fine motor control', 'Sleep issues', 'Picky eating', 'Difficulty with peers'];
  const goalPool: Record<TherapyType, string[]> = {
    speech: ['Use 2-word phrases', 'Respond to name consistently', 'Follow 2-step instructions', 'Improve articulation of /s/ /k/'],
    ot: ['Hold pencil with tripod grip', 'Tolerate varied textures', 'Button own shirt', 'Improve balance on one leg'],
    behavior: ['Reduce tantrums to <2/week', 'Transition between tasks calmly', 'Wait for turn in play', 'Use calm-down strategy'],
    special_ed: ['Recognise letters A-Z', 'Count objects to 20', 'Sit 10 min for table task', 'Match colours and shapes'],
  };
  const alertTypes = ['fever', 'regression', 'aggression', 'seizure', 'sleep_issue', 'injury', 'emotional_stress', 'other'] as const;
  const alertCategory: Record<string, string> = {
    fever: 'health', regression: 'regression', aggression: 'behavior', seizure: 'health',
    sleep_issue: 'health', injury: 'health', emotional_stress: 'tantrum', other: 'other',
  };
  const activitiesPool = ['Picture cards', 'Play-dough', 'Sensory bin', 'Story reading', 'Puzzle', 'Peg board', 'Swing', 'Role play', 'Bubble blowing', 'Matching game'];
  const centerLocation = { lat: 26.2183, lng: 78.1828, address: 'NaiviSense Center, Gwalior (sample)' };

  // ---- children ----------------------------------------------------------
  const weekStarts: Date[] = [];
  for (let d = DATA_START; d <= addDays(DATA_END, FUTURE_WEEKS * 7); d = addDays(d, 7)) weekStarts.push(d);
  const monthKey = (d: Date) => `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, '0')}`;

  for (let i = 0; i < studentCount; i++) {
    const gender = chance(0.7) ? 'boy' : 'girl';
    const childFirst = pick(gender === 'boy' ? firstBoys : firstGirls);
    const lastName = pick(lastNames);
    const ageYears = clamp(Math.round(between(2.5, 12)), 3, 12);
    const dob = addDays(DATA_END, -Math.round(ageYears * 365.25 + between(-150, 150)));
    const diagnosis = [weighted(diagnoses, diagWeights)];
    if (chance(0.25)) diagnosis.push(pick(diagnoses.filter((d) => d !== diagnosis[0])));
    const severity = weighted(['mild', 'moderate', 'severe'] as const, [35, 45, 20]);
    const sevPenalty = severity === 'mild' ? 0 : severity === 'moderate' ? 10 : 20;

    // Latent traits (not stored; they shape everything downstream).
    const involvement = weighted(['low', 'medium', 'high'] as const, [25, 45, 30]);
    const invNum = involvement === 'low' ? 0.35 : involvement === 'medium' ? 0.65 : 0.92;
    const responsiveness = clamp(between(0.5, 1.15) - (severity === 'severe' ? 0.15 : 0), 0.3, 1.2);
    const attendProb = clamp(0.62 + invNum * 0.33 + between(-0.06, 0.06), 0.5, 0.98);

    // Enrollment spread: ~60% already enrolled before data window.
    const enrollOffset = chance(0.6) ? -int(15, 200) : int(0, 150);
    const enrolled = addDays(DATA_START, enrollOffset);
    const effectiveStart = enrolled < DATA_START ? DATA_START : enrolled;

    // Parent
    const parentUserId = mkUser(`${pick(parentFirst)} ${lastName}`, 'parent', `parent${i + 1}@example.test`);
    const childId = oid();

    // Therapy plan: 1-3 types, each with a specific therapist and 2 weekdays.
    const typeCount = weighted([1, 2, 3], [25, 50, 25]);
    const types = [...THERAPY_TYPES].sort(() => rnd() - 0.5).slice(0, typeCount);
    const plan = types.map((type) => {
      const pool = therapists.filter((t) => t.type === type);
      const th = pick(pool);
      const days = [1, 2, 3, 4, 5].sort(() => rnd() - 0.5).slice(0, int(2, 3)).sort();
      const mode = chance(0.25) ? ('online' as const) : ('offline' as const);
      const startHour = int(9, 16);
      return { type, th, days, mode, startHour };
    });

    const caseNotes = diagnosis.join(', ');
    const baselineComm = weighted(['non_verbal', 'single_words', 'phrases', 'sentences'] as const, [severity === 'severe' ? 50 : 15, 30, 35, severity === 'mild' ? 30 : 8]);

    out.children.push({
      _id: childId, name: `${childFirst} ${lastName}`, dob, gender, diagnosis, severity,
      primary_concerns: [...concernPool].sort(() => rnd() - 0.5).slice(0, int(2, 3)),
      therapy_targets: plan.flatMap((p) => goalPool[p.type].slice(0, 1)),
      therapists: plan.map((p) => ({
        therapist_id: p.th.id, therapy_type: p.type,
        schedule: [{ enrollment_mode: p.mode, days: p.days, from_time: `${String(p.startHour).padStart(2, '0')}:00`, to_time: `${String(p.startHour).padStart(2, '0')}:45` }],
        upcoming_sessions: [],
      })),
      parent_id: parentUserId, center_id: centerId,
      medical: {
        birth_history: weighted(['normal', 'premature', 'complications'] as const, [65, 22, 13]),
        milestones_delay: chance(0.7), hearing_issues: chance(0.08), vision_issues: chance(0.1),
        current_medications: chance(0.2) ? [pick(['Melatonin', 'Methylphenidate', 'Risperidone'])] : [],
      },
      emergency_contact: { name: `${pick(parentFirst)} ${lastName}`, phone: nextPhone() },
      documents: [],
      home_context: {
        primary_caregiver: pick(['mother', 'father', 'grandparent']),
        screen_time_hours: Math.round(clamp(between(0.5, 5) - invNum, 0.3, 6) * 10) / 10,
        play_type: pick(['alone', 'guided', 'group']),
        parent_involvement: involvement,
      },
      goals: { priorities: plan.map((p) => p.type), timeline_months: pick([6, 9, 12]) },
      parent_email: `parent${i + 1}@example.test`,
      consent_record: { given_at: enrolled, given_by: 'parent' },
      functional_baseline: {
        communication_level: baselineComm,
        attention_span_mins: int(3, severity === 'mild' ? 15 : 8),
        social_interaction: pick(['avoids', 'parallel', 'initiates']),
        motor_skills: pick(['delayed', 'age_appropriate', 'advanced']),
        behavior_pattern: caseNotes,
      },
      nutrition_profile: {
        food_allergies: chance(0.12) ? [pick(['peanut', 'dairy', 'gluten'])] : [],
        picky: chance(0.5),
        height_cm: Math.round(80 + ageYears * 6 + between(-4, 4)),
        weight_kg: Math.round((10 + ageYears * 2.6 + between(-2, 2)) * 10) / 10,
      },
      enrolled_at: enrolled,
      created_at: enrolled, updated_at: enrolled, ...tag,
    });
    out.parent_profiles.push({
      _id: oid(), user_id: parentUserId, center_id: centerId,
      children: [{ child_id: childId, therapists: plan.map((p) => ({ therapist_id: p.th.id, therapy_type: p.type, upcoming_sessions: [] })) }],
      created_at: enrolled, updated_at: enrolled, ...tag,
    });

    // ---- assessments: initial + monthly snapshots ------------------------
    const baseDomain: Record<string, number> = {};
    for (const d of DOMAINS) baseDomain[d] = clamp(between(28, 62) - sevPenalty * 0.8 + (diagnosis[0].startsWith('Speech') && d.includes('language') ? -8 : 0), 8, 85);
    const therapyDomains = new Set(plan.flatMap((p) => TYPE_DOMAINS[p.type]));
    const snapshotDates: Date[] = [enrolled];
    for (let d = addDays(enrolled, 30); d <= DATA_END; d = addDays(d, 30)) snapshotDates.push(d);

    // Mean attendance fraction (expected) so improvement tracks real exposure.
    const monthlyGain = 1.9 * responsiveness * attendProb * (0.6 + invNum * 0.6);
    const snaps = snapshotDates.map((date, idx) => {
      const domain_scores: Record<string, number> = {};
      for (const d of DOMAINS) {
        const treated = therapyDomains.has(d);
        const noise = between(-2.2, 2.2);
        const gain = idx * monthlyGain * (treated ? 1.5 : 0.45);
        domain_scores[d] = Math.round(clamp(baseDomain[d] + gain + noise, 5, 98) * 10) / 10;
      }
      const vals = Object.values(domain_scores);
      const overall = Math.round((vals.reduce((s, x) => s + x, 0) / vals.length) * 10) / 10;
      const risk_level = overall < 40 ? 'red' : overall < 62 ? 'amber' : 'green';
      return {
        type: idx === 0 ? 'initial' : idx % 3 === 0 ? 'quarterly' : 'monthly',
        date, assessed_by: pick(plan).th.id, is_complete: true, domain_data: {},
        domain_scores, overall_score_pct: overall, risk_level,
        developmental_quotient: Math.round(clamp(overall * 0.95 + between(-3, 3), 10, 120)),
        general_notes: `Sample ${idx === 0 ? 'initial' : 'follow-up'} assessment`,
      };
    });
    out.assessments.push({
      _id: oid(), child_id: childId, initial: snaps[0], previous: snaps.length > 1 ? snaps[snaps.length - 2] : null,
      latest: snaps[snaps.length - 1], created_at: enrolled, updated_at: snaps[snaps.length - 1].date, ...tag,
    });
    snaps.forEach((s, idx) => out.assessment_history.push({ _id: oid(), child_id: childId, seq: idx, ...s, created_at: s.date, ...tag }));

    // ---- sessions + attendance + notes -----------------------------------
    const progressAt = (date: Date) => clamp((date.getTime() - enrolled.getTime()) / (DATA_END.getTime() - DATA_START.getTime()), 0, 1.2);
    const sessionIdsFuture: { th: ObjectId; type: TherapyType; sid: ObjectId; at: Date; end: Date; mode: string }[] = [];
    let sessionsInWeek = new Map<string, number>(); // week key -> attended
    let attendedTotal = 0;

    for (const p of plan) {
      for (const ws of weekStarts) {
        for (const dow of p.days) {
          const day = addDays(ws, dow - 1);
          if (day < effectiveStart) continue;
          const at = withTime(day, p.startHour);
          const end = new Date(at.getTime() + 45 * 60000);
          const isFuture = at > DATA_END;
          const sid = oid();
          const mode = p.mode;
          const base = {
            _id: sid, child_id: childId, therapist_id: p.th.id, scheduled_at: at, end_at: end,
            type: p.type, mode, duration_min: 45,
            offline_location: mode === 'offline' ? centerLocation.address : undefined,
            meeting_link: mode === 'online' ? `https://meet.example.test/${sid.toString().slice(-8)}` : undefined,
            created_at: addDays(at, -7), updated_at: end, ...tag,
          };
          if (isFuture) {
            out.sessions.push({ ...base, status: 'scheduled' });
            sessionIdsFuture.push({ th: p.th.id, type: p.type, sid, at, end, mode });
            continue;
          }
          // seasonal dip: Diwali week in November, monsoon bump in July
          const seasonal = at.getUTCMonth() === 10 && at.getUTCDate() >= 8 && at.getUTCDate() <= 14 ? -0.15 : at.getUTCMonth() === 6 ? -0.04 : 0;
          const r = rnd();
          const pAttend = clamp(attendProb + seasonal, 0.3, 0.99);
          const attStatus = r < pAttend ? (chance(0.1) ? 'late' : 'present') : 'absent';
          if (attStatus === 'absent') {
            out.sessions.push({ ...base, status: 'cancelled' });
            out.attendances.push({
              _id: oid(), child_id: childId, session_id: sid, date: at, status: 'absent', marked_by: p.th.id,
              source: 'manual_override', notes: pick(['Illness', 'Family travel', 'No reason given', 'Transport issue']),
              created_at: end, updated_at: end, ...tag,
            });
            continue;
          }
          attendedTotal++;
          const key = monthKey(at);
          sessionsInWeek.set(key, (sessionsInWeek.get(key) ?? 0) + 1);
          const prog = progressAt(at);
          const level = (b: number) => Math.round(clamp(b + prog * 3.2 * responsiveness * p.th.skill + between(-1.3, 1.3), 1, 10));
          const sevBase = severity === 'mild' ? 5 : severity === 'moderate' ? 4 : 3;
          const moodScore = level(sevBase);
          const mood = moodScore >= 8 ? 'excited' : moodScore >= 6 ? 'happy' : moodScore >= 4 ? 'calm' : 'sad';
          out.sessions.push({
            ...base, status: 'completed',
            notes: {
              mood, attention_score: level(sevBase), communication_score: level(sevBase - (p.type === 'speech' ? 0.5 : 0)),
              motor_score: level(sevBase), behavior_score: level(sevBase + 0.5),
              activities: [...activitiesPool].sort(() => rnd() - 0.5).slice(0, int(2, 3)),
              what_worked: pick(['Visual schedule', 'Short tasks', 'Rewards chart', 'Music cues']),
              what_didnt_work: chance(0.4) ? pick(['Long instructions', 'Noisy room', 'Transition without warning']) : undefined,
              homework: pick(['Practice 10 min daily', 'Flashcards', 'Sensory play']),
              tantrums_observed: chance(0.15 * (1.2 - prog * 0.5)) ? 'Brief tantrum during transition' : undefined,
              follow_up_required: chance(0.1), submitted_at: end,
            },
          });
          out.attendances.push({
            _id: oid(), child_id: childId, session_id: sid, date: at, status: attStatus, marked_by: p.th.id,
            source: mode === 'online' ? 'google_meet' : 'geo', location: mode === 'offline' ? centerLocation : undefined,
            created_at: at, updated_at: at, ...tag,
          });
        }
      }
    }
    // upcoming sessions on the child doc (as the app does)
    const childDoc = out.children[out.children.length - 1] as { therapists: { therapist_id: ObjectId; upcoming_sessions: unknown[] }[] };
    for (const fs of sessionIdsFuture) {
      childDoc.therapists.find((t) => t.therapist_id.equals(fs.th))?.upcoming_sessions.push({ session_id: fs.sid, scheduled_at: fs.at, end_at: fs.end, mode: fs.mode, status: 'scheduled' });
    }
    void sessionsInWeek; void attendedTotal;

    // ---- goals ------------------------------------------------------------
    const lastOverallGain = snaps[snaps.length - 1].overall_score_pct - snaps[0].overall_score_pct;
    plan.forEach((p, gi) => {
      goalPool[p.type].slice(0, int(1, 2)).forEach((title) => {
        const created = addDays(enrolled, int(0, 20));
        const done = chance(clamp(lastOverallGain / 22, 0.05, 0.7));
        const status = done ? 'completed' : chance(0.1) ? 'paused' : chance(0.85) ? 'active' : 'proposed';
        out.goals.push({
          _id: oid(), child_id: childId, created_by: p.th.id, title, priority: gi + 1, status,
          accepted_by: status === 'proposed' ? undefined : parentUserId, accepted_at: status === 'proposed' ? undefined : addDays(created, 3),
          target_date: addDays(created, 30 * (childDoc ? int(3, 9) : 6)), created_at: created, updated_at: addDays(created, 14), ...tag,
        });
      });
    });

    // ---- alerts (higher for severe, lower with involvement) ---------------
    const alertRatePerMonth = (severity === 'severe' ? 0.9 : severity === 'moderate' ? 0.55 : 0.3) * (1.1 - invNum * 0.4);
    const monthsSpan = Math.max(1, (DATA_END.getTime() - effectiveStart.getTime()) / (30 * 86400000));
    const alertCount = Math.round(alertRatePerMonth * monthsSpan * between(0.6, 1.4));
    for (let a = 0; a < alertCount; a++) {
      const when = addDays(effectiveStart, Math.floor(rnd() * ((DATA_END.getTime() - effectiveStart.getTime()) / 86400000)));
      const type = weighted(alertTypes, [10, 15, 18, 3, 16, 8, 22, 8]);
      const sev = type === 'seizure' ? 'high' : weighted(['low', 'medium', 'high'] as const, [40, 40, 20]);
      const recent = (DATA_END.getTime() - when.getTime()) / 86400000 < 5;
      const status = recent && chance(0.6) ? 'open' : chance(0.88) ? 'resolved' : 'seen';
      const ack = addDays(when, 0); ack.setTime(when.getTime() + (sev === 'high' ? between(0.2, 3) : between(1, 30)) * 3600000);
      const res = status === 'resolved' ? new Date(ack.getTime() + (sev === 'high' ? between(2, 30) : between(6, 120)) * 3600000) : null;
      const raisedByParent = chance(0.65);
      out.alerts.push({
        _id: oid(), child_id: childId, raised_by: raisedByParent ? parentUserId : pick(plan).th.id, type,
        description: `Sample ${type.replace('_', ' ')} alert`, severity: sev, priority: sev === 'high' ? 'high' : 'normal',
        category: alertCategory[type], source: raisedByParent ? 'parent' : 'therapist', status,
        resolved_by: status === 'resolved' ? pick(plan).th.id : undefined, resolution_note: status === 'resolved' ? 'Addressed with parent guidance' : undefined,
        acknowledged_at: status === 'open' ? null : ack, resolved_at: res, created_at: when, ...tag,
      });
    }

    // ---- concerns ---------------------------------------------------------
    for (let c = 0; c < int(0, 3); c++) {
      const when = addDays(effectiveStart, Math.floor(rnd() * 150));
      const resolved = chance(0.7);
      out.concerns.push({
        _id: oid(), child_id: childId, created_by: parentUserId, created_by_role: 'parent',
        category: pick(['tantrum', 'behavior', 'health', 'regression', 'activity', 'other']),
        description: 'Sample parent concern', status: resolved ? 'resolved' : 'open',
        resolved_by: resolved ? pick(plan).th.id : undefined, resolution: resolved ? 'Discussed in session' : undefined,
        resolved_at: resolved ? addDays(when, int(1, 7)) : undefined, created_at: when, updated_at: when, ...tag,
      });
    }

    // ---- payments: monthly subscription + one-time assessment fee ---------
    const fee = Math.round((6000 + typeCount * 3500 + (severity === 'severe' ? 1500 : 0)) / 100) * 100;
    out.payments.push({
      _id: oid(), parent_id: parentUserId.toString(), child_id: childId.toString(), type: 'assessment_fee',
      amount_paise: 150000, currency: 'INR', status: 'paid', paid_at: enrolled, created_at: enrolled, updated_at: enrolled, ...tag,
    });
    for (let m = new Date(Date.UTC(effectiveStart.getUTCFullYear(), effectiveStart.getUTCMonth(), 1)); m <= DATA_END; m = new Date(Date.UTC(m.getUTCFullYear(), m.getUTCMonth() + 1, 1))) {
      const due = new Date(Math.max(m.getTime(), effectiveStart.getTime()));
      const isCurrent = monthKey(m) === monthKey(DATA_END);
      const failP = 0.04 + (1 - invNum) * 0.05;
      const status = isCurrent && chance(0.45) ? 'pending' : weighted(['paid', 'pending', 'failed', 'refunded'] as const, [100 - failP * 100 - 10, 7, failP * 100, 3]);
      out.payments.push({
        _id: oid(), parent_id: parentUserId.toString(), child_id: childId.toString(), type: 'subscription',
        amount_paise: fee * 100, currency: 'INR', status,
        razorpay_order_id: `order_syn_${oid().toString().slice(-10)}`,
        razorpay_payment_id: status === 'paid' || status === 'refunded' ? `pay_syn_${oid().toString().slice(-10)}` : undefined,
        paid_at: status === 'paid' || status === 'refunded' ? addDays(due, int(0, 9)) : undefined,
        created_at: due, updated_at: due, ...tag,
      });
    }

    // ---- home engagement logs (weekly) ------------------------------------
    const dietPlanId = oid();
    const homePlanId = oid();
    for (const ws of weekStarts) {
      if (ws < effectiveStart || ws > DATA_END) continue;
      const taskCount = Math.round(clamp(invNum * 5 + between(-1.5, 1.5), 0, 7));
      for (let t = 0; t < taskCount; t++) {
        const at = withTime(addDays(ws, int(0, 6)), int(16, 20), int(0, 59));
        if (at > DATA_END) continue;
        out.home_task_logs.push({
          _id: oid(), home_plan_id: homePlanId, task_id: `task_${int(1, 6)}`, child_id: childId, logged_by: parentUserId, logged_at: at,
          image_url: 'https://example.test/img.jpg', status: weighted(['approved', 'pending', 'rejected'] as const, [75, 15, 10]),
          verification_id: null, created_at: at, updated_at: at, ...tag,
        });
      }
      const mealCount = Math.round(clamp(invNum * 12 + between(-3, 3), 0, 21));
      for (let m = 0; m < mealCount; m++) {
        const at = withTime(addDays(ws, int(0, 6)), pick([8, 13, 19]), int(0, 59));
        if (at > DATA_END) continue;
        out.meal_logs.push({
          _id: oid(), diet_plan_id: dietPlanId, meal_id: pick(['breakfast', 'lunch', 'dinner']), child_id: childId, logged_by: parentUserId,
          logged_at: at, status: weighted(['approved', 'pending', 'rejected'] as const, [78, 15, 7]), verification_id: null,
          created_at: at, updated_at: at, ...tag,
        });
      }
    }
  }
  return out;
}
