export type Group = 'Thriving' | 'Efficient' | 'Under-served' | 'At-risk';
export type Involvement = 'low' | 'medium' | 'high';

export interface Child {
  code: string;
  group: Group;
  fees: number;
  progress: number;
  valueIndex: number;
  attendance: number;
  improvement: number;
  sessions: number;
  initialScore: number;
  latestScore: number;
  initialRisk: string;
  latestRisk: string;
  alerts: number;
  openAlerts: number;
  outstanding: number;
  monthlyFee: number;
  homeTasksPerWeek: number;
  goalsCompleted: number;
  goalsTotal: number;
  churnRisk: boolean;
  diagnosis: string;
  severity: 'mild' | 'moderate' | 'severe';
  involvement: Involvement;
  ageBand: string;
  gender: string;
  ageYears: number;
  therapies: string[];
}

export interface Therapist {
  name: string;
  specialty: string;
  caseload: number;
  sessions: number;
  fees: number;
  value_index: number;
  progress: number;
}

export interface GroupStat {
  label: string;
  children?: number;
  sessions?: number;
  fees: number;
  progress_pts: number;
  value_index: number;
}

export interface Dashboard {
  meta: {
    students: number;
    therapists: number;
    period: string;
    medianFee: number;
    medianProgress: number;
    generated: string;
  };
  kpi: {
    students: number;
    therapists: number;
    sessions_past: number;
    sessions_attended: number;
    attendance_rate: number;
    billed_inr: number;
    collected_inr: number;
    outstanding_inr: number;
    collection_rate: number;
    avg_improvement_pts: number;
    churn_risk_children: number;
    red_risk_children: number;
    risk_improved_children: number;
    failed_payments: number;
    alerts_total: number;
    alerts_open: number;
  };
  quadrants: Record<Group, number>;
  children: Child[];
  therapists: Therapist[];
  therapyTypes: GroupStat[];
  involvement: (GroupStat & {
    attendance: number;
    improvement_pts: number;
    home_tasks_per_week: number;
    collection_rate: number;
  })[];
  bySeverity: GroupStat[];
  byDiagnosis: GroupStat[];
  byAgeBand: GroupStat[];
  byFeeTier: GroupStat[];
  feeTierDetail: Record<string, { avg_attendance: number; avg_improvement_pts: number }>;
  correlations: {
    attendanceVsImprovement: number;
    homeTasksVsImprovement: number;
    monthlyFeeVsImprovement: number;
    involvementVsImprovement: number;
  };
  domains: { domain: string; group: string; gain: number }[];
  alerts: {
    sla: {
      severity: string;
      alerts: number;
      avg_hrs_ack: number;
      avg_hrs_resolve: number;
      ack_within_4h_pct: number;
    }[];
    byType: { type: string; count: number }[];
    perChildBySeverity: Record<string, number>;
  };
  revenue: {
    monthly: { month: string; billed: number; collected: number; attendance: number }[];
    byStatus: { status: string; count: number; inr: number }[];
    topOutstanding: { child: string; outstanding_inr: number }[];
  };
  engagement: Record<string, number>;
}
