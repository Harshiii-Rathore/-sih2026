import {
  DashboardData,
  ProjectItem,
  ProjectDetail,
  AgencyItem,
  MapMarkerItem,
  RealAllocationResponse,
  AuditLogItem,
  UserSession
} from "./types";

const API_BASE = "http://localhost:8000/api";

export async function fetchDashboard(): Promise<DashboardData> {
  const res = await fetch(`${API_BASE}/dashboard`);
  if (!res.ok) throw new Error("Failed to fetch dashboard data");
  return res.json();
}

export async function fetchProjects(params: {
  page?: number;
  pageSize?: number;
  search?: string;
  state?: string;
  district?: string;
  category?: string;
  riskLevel?: string;
  status?: string;
  sortBy?: string;
  sortDir?: string;
}): Promise<{ items: ProjectItem[]; total: number; page: number; pageSize: number; totalPages: number }> {
  const query = new URLSearchParams();
  if (params.page) query.set("page", params.page.toString());
  if (params.pageSize) query.set("page_size", params.pageSize.toString());
  if (params.search) query.set("search", params.search);
  if (params.state && params.state !== "ALL") query.set("state", params.state);
  if (params.district && params.district !== "ALL") query.set("district", params.district);
  if (params.category && params.category !== "ALL") query.set("category", params.category);
  if (params.riskLevel && params.riskLevel !== "ALL") query.set("risk_level", params.riskLevel);
  if (params.status && params.status !== "ALL") query.set("status", params.status);
  if (params.sortBy) query.set("sort_by", params.sortBy);
  if (params.sortDir) query.set("sort_dir", params.sortDir);

  const res = await fetch(`${API_BASE}/projects?${query.toString()}`);
  if (!res.ok) throw new Error("Failed to fetch projects");
  return res.json();
}

export async function fetchProjectDetails(projectId: string): Promise<ProjectDetail> {
  const res = await fetch(`${API_BASE}/projects/${projectId}`);
  if (!res.ok) throw new Error(`Failed to fetch details for ${projectId}`);
  return res.json();
}

export async function fetchMapMarkers(params?: { state?: string; riskLevel?: string; category?: string }): Promise<MapMarkerItem[]> {
  const query = new URLSearchParams();
  if (params?.state && params.state !== "ALL") query.set("state", params.state);
  if (params?.riskLevel && params.riskLevel !== "ALL") query.set("risk_level", params.riskLevel);
  if (params?.category && params.category !== "ALL") query.set("category", params.category);

  const res = await fetch(`${API_BASE}/map?${query.toString()}`);
  if (!res.ok) throw new Error("Failed to fetch map points");
  return res.json();
}

export async function fetchAgencies(): Promise<AgencyItem[]> {
  const res = await fetch(`${API_BASE}/agencies`);
  if (!res.ok) throw new Error("Failed to fetch agencies");
  return res.json();
}

export async function fetchAgencyProfile(agencyName: string): Promise<{ agency: AgencyItem; projects: any[] }> {
  const res = await fetch(`${API_BASE}/agencies/${encodeURIComponent(agencyName)}`);
  if (!res.ok) throw new Error(`Failed to fetch profile for ${agencyName}`);
  return res.json();
}

export async function fetchRealAllocations(state?: string): Promise<RealAllocationResponse> {
  const query = state && state !== "ALL" ? `?state=${encodeURIComponent(state)}` : "";
  const res = await fetch(`${API_BASE}/allocations${query}`);
  if (!res.ok) throw new Error("Failed to fetch real allocations");
  return res.json();
}

export async function fetchAuditLogs(): Promise<AuditLogItem[]> {
  const res = await fetch(`${API_BASE}/audit-logs`);
  if (!res.ok) throw new Error("Failed to fetch audit logs");
  return res.json();
}

export async function loginUser(username: string, password: string): Promise<UserSession> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });
  if (!res.ok) throw new Error("Authentication failed");
  return res.json();
}

export function getReportDownloadUrl(projectId: string): string {
  return `${API_BASE}/projects/${projectId}/report`;
}
