export interface RiskContributingFactor {
  dimension: string;
  score: number;
  flag_note: string;
}

export interface SimilarProject {
  project_id: string;
  work_title: string;
  category: string;
  distance_km: number;
  text_similarity_pct: number;
  sanction_amount: number;
  status: string;
}

export interface ProjectEvidence {
  sanction_amount: number;
  expenditure_amount: number;
  peer_median_cost?: number;
  cost_deviation_pct?: number;
  expected_months?: number;
  elapsed_months?: number;
  delay_percentage?: number;
  payment_tranches?: number;
  utilization_pct?: number;
  agency_projects_count?: number;
  agency_cost_premium_pct?: number;
  agency_value_deviation_pct?: number;
  agency_concentration_pct?: number;
  compliance_violations?: string[];
  explanation?: string;
}

export interface ProjectRisk {
  overall_risk_score: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  cost_risk_score: number;
  timeline_risk_score: number;
  expenditure_risk_score: number;
  overlap_risk_score: number;
  agency_risk_score: number;
  compliance_risk_score: number;
  contributing_factors: RiskContributingFactor[];
  evidence: ProjectEvidence;
  recommended_action: string;
  similar_projects: SimilarProject[];
}

export interface PaymentRecord {
  date: string;
  amount: number;
}

export interface ProjectItem {
  project_id: string;
  work_title: string;
  work_category: string;
  state: string;
  district: string;
  constituency: string;
  mp_name: string;
  sanction_amount: number;
  expenditure_amount: number;
  status: string;
  implementing_agency: string;
  sanction_date: string;
  expected_completion_date: string;
  risk_score: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  top_factor: string;
  data_source: string;
}

export interface ProjectDetail {
  project: {
    project_id: string;
    work_title: string;
    work_description: string;
    work_category: string;
    state: string;
    district: string;
    constituency: string;
    mp_name: string;
    sanction_amount: number;
    expenditure_amount: number;
    sanction_date: string;
    expected_completion_date: string;
    actual_completion_date?: string | null;
    status: string;
    implementing_agency: string;
    latitude: number;
    longitude: number;
    number_of_payments: number;
    payments: PaymentRecord[];
    data_source: string;
  };
  risk: ProjectRisk;
}

export interface DashboardKPIs {
  total_projects: number;
  total_sanction_amount: number;
  total_expenditure_amount: number;
  utilization_percentage: number;
  critical_projects: number;
  high_risk_projects: number;
  medium_risk_projects?: number;
  low_risk_projects?: number;
  normal_tolerance_count?: number;
  projects_requiring_verification: number;
}

export interface RiskDistributionItem {
  name: string;
  count: number;
  level: string;
  color: string;
}

export interface CategoryDistributionItem {
  category: string;
  count: number;
  sanction_amount: number;
  expenditure_amount: number;
}

export interface StateDistributionItem {
  state: string;
  total_projects: number;
  total_sanction: number;
  high_risk_count: number;
}

export interface DashboardData {
  kpis: DashboardKPIs;
  risk_distribution: RiskDistributionItem[];
  category_distribution: CategoryDistributionItem[];
  projects_by_state: StateDistributionItem[];
  ai_insights: string[];
  flagship_project_id: string;
}

export interface AgencyItem {
  agency_name: string;
  district: string;
  state: string;
  total_projects: number;
  total_sanctioned_amount: number;
  average_project_value: number;
  high_risk_projects_count: number;
  risk_percentage: number;
  primary_category: string;
}

export interface MapMarkerItem {
  project_id: string;
  work_title: string;
  category: string;
  state: string;
  district: string;
  latitude: number;
  longitude: number;
  sanction_amount: number;
  expenditure_amount: number;
  status: string;
  risk_score: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  main_anomaly: string;
}

export interface RealAllocationItem {
  sr_no: number;
  state: string;
  mp_name: string;
  constituency: string;
  allocated_amount: number;
}

export interface RealAllocationResponse {
  total_mps: number;
  total_allocated_limit_inr: number;
  data_source: string;
  csv_filename: string;
  state_breakdown: { state: string; mp_count: number; total_allocated: number }[];
  allocations: RealAllocationItem[];
}

export interface AuditLogItem {
  id: number;
  user_name: string;
  user_role: string;
  action: string;
  project_id?: string | null;
  timestamp: string;
  details?: string | null;
}

export interface UserSession {
  token: string;
  username: string;
  full_name: string;
  role: string;
  department: string;
}
