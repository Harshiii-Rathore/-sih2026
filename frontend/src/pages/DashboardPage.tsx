import React, { useEffect, useState } from "react";
import {
  FolderKanban,
  AlertTriangle,
  Flame,
  CheckCircle2,
  Sparkles,
  ArrowRight,
  TrendingUp,
  BarChart3,
  MapPin,
  Coins
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  PieChart,
  Pie,
} from "recharts";
import { DashboardData } from "../types";
import { fetchDashboard } from "../api";
import { MetricCard } from "../components/MetricCard";
import { RiskBadge } from "../components/RiskBadge";

interface DashboardPageProps {
  onSelectProject: (projectId: string) => void;
  onNavigateToProjects: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  onSelectProject,
  onNavigateToProjects,
}) => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboard()
      .then((res) => setData(res))
      .catch((err) => console.error("Error fetching dashboard:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm font-semibold text-slate-600">Loading National MPLADS Analytics...</p>
        </div>
      </div>
    );
  }

  const kpis = data.kpis;
  const formatCrores = (val: number) => `₹ ${(val / 10000000).toFixed(2)} Cr`;

  return (
    <div className="space-y-6 pb-12">
      {/* Top Banner / Purpose Headline */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-700 text-xs font-bold uppercase tracking-wider">
              Executive Overview
            </span>
            <span className="text-xs text-slate-400 font-medium">National Scheme Surveillance</span>
          </div>
          <h1 className="mt-1 text-2xl font-black text-slate-900 tracking-tight">
            MPLADS Monitoring & AI Anomaly Intelligence
          </h1>
          <p className="mt-1 text-sm text-slate-600 max-w-3xl">
            Decision-support intelligence engine continuously screening project costs, timeline delays,
            GIS spatial overlaps, and implementing agency concentration to prioritize audits.
          </p>
        </div>

        {/* Action Button */}
        <button
          onClick={onNavigateToProjects}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold shadow-sm shadow-blue-600/20 transition shrink-0"
        >
          <span>View All Monitored Projects</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Flagship Hackathon Demo Showcase Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 p-6 text-white shadow-lg border border-indigo-900/50">
        <div className="absolute right-0 top-0 translate-x-8 -translate-y-8 w-64 h-64 bg-red-600/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-5">
          <div className="space-y-2">
            <div className="flex items-center gap-2.5">
              <span className="px-2.5 py-0.5 rounded-full bg-red-500/20 text-red-300 border border-red-500/30 font-mono text-xs font-bold tracking-wider animate-pulse flex items-center gap-1.5">
                <Flame className="w-3.5 h-3.5 text-red-400" />
                HACKATHON DEMO SHOWCASE CASE
              </span>
              <span className="text-xs font-mono text-slate-400 font-bold">PROJECT ID: MPL-DEMO-001</span>
            </div>
            <h2 className="text-xl font-black tracking-tight text-white">
              Construction of Community Hall at Village Khed
            </h2>
            <p className="text-xs text-slate-300 max-w-2xl leading-relaxed">
              Prioritized by multi-signal anomaly engine: <span className="text-red-300 font-semibold">+104% cost anomaly</span> vs category median, <span className="text-amber-300 font-semibold">+83% execution delay</span>, and <span className="text-blue-300 font-semibold">potential spatial overlap (0.7 km away, 87% similarity)</span>.
            </p>
          </div>

          <div className="flex items-center gap-4 shrink-0">
            <div className="text-right">
              <div className="text-xs font-medium text-slate-400 uppercase tracking-wider">AI Risk Score</div>
              <div className="text-3xl font-black text-red-400 font-mono">80.3<span className="text-lg text-slate-400">/100</span></div>
              <div className="text-[11px] font-bold text-red-300 uppercase tracking-wide">Critical Risk</div>
            </div>

            <button
              onClick={() => onSelectProject(data.flagship_project_id || "MPL-DEMO-001")}
              className="px-5 py-3 rounded-xl bg-red-600 hover:bg-red-500 text-white font-bold text-xs uppercase tracking-wider shadow-lg shadow-red-600/30 transition flex items-center gap-2"
            >
              <span>Investigate Case</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
        <MetricCard
          title="Monitored Projects"
          value={kpis.total_projects.toLocaleString()}
          subtitle="Total National Baseline"
          icon={FolderKanban}
          variant="highlight"
        />
        <MetricCard
          title="Sanctioned Limit"
          value={formatCrores(kpis.total_sanction_amount)}
          subtitle="Total Administrative Value"
          icon={Coins}
        />
        <MetricCard
          title="Total Disbursed"
          value={formatCrores(kpis.total_expenditure_amount)}
          subtitle={`${kpis.utilization_percentage}% Fund Utilization`}
          icon={TrendingUp}
        />
        <MetricCard
          title="Requires Verification"
          value={kpis.projects_requiring_verification.toLocaleString()}
          subtitle={`${kpis.critical_projects} Critical + ${kpis.high_risk_projects} High`}
          icon={AlertTriangle}
          variant="high"
          onClick={onNavigateToProjects}
        />
        <MetricCard
          title="Critical Priority"
          value={kpis.critical_projects.toLocaleString()}
          subtitle="Immediate Audit Action"
          icon={Flame}
          variant="critical"
          onClick={onNavigateToProjects}
        />
        <MetricCard
          title="Normal Tolerance"
          value={(kpis.normal_tolerance_count ?? (kpis.total_projects - kpis.projects_requiring_verification)).toLocaleString()}
          subtitle={`${kpis.low_risk_projects ?? 0} Low + ${kpis.medium_risk_projects ?? 0} Medium`}
          icon={CheckCircle2}
          variant="low"
        />
      </div>

      {/* KPI Audit Reconciliation Status Bar */}
      <div className="px-4 py-2.5 rounded-xl bg-slate-50 border border-slate-200/80 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-600">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
          <span className="font-bold text-slate-700 uppercase tracking-wider text-[11px]">Triage Integrity Equation:</span>
          <span className="font-mono font-semibold text-slate-900">
            {kpis.total_projects.toLocaleString()} Monitored Works = {(kpis.normal_tolerance_count ?? (kpis.total_projects - kpis.projects_requiring_verification)).toLocaleString()} Normal Tolerance ({kpis.low_risk_projects ?? 0} Low + {kpis.medium_risk_projects ?? 0} Medium) + {kpis.projects_requiring_verification.toLocaleString()} Requires Verification ({kpis.critical_projects} Critical + {kpis.high_risk_projects} High)
          </span>
        </div>
        <span className="text-[11px] text-slate-400 font-medium">100% Deterministic Portfolio Coverage</span>
      </div>

      {/* AI Insights & Dynamic Engine Intelligence */}
      <div className="bg-gradient-to-br from-blue-900 to-slate-900 text-white p-6 rounded-2xl border border-blue-800 shadow-md">
        <div className="flex items-center gap-2 mb-3">
          <div className="p-1.5 rounded-lg bg-blue-500/20 text-blue-400 border border-blue-400/30">
            <Sparkles className="w-4 h-4 text-blue-400 animate-pulse" />
          </div>
          <h3 className="font-bold text-sm tracking-wide text-white uppercase">
            NIRIKSHAN Engine Insights (Computed Live From Dataset)
          </h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 text-xs">
          {data.ai_insights.map((insight, idx) => (
            <div
              key={idx}
              className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/80 flex items-start gap-2.5"
            >
              <div className="w-2 h-2 rounded-full bg-blue-400 mt-1 shrink-0" />
              <p className="text-slate-200 leading-relaxed font-medium">{insight}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk Distribution Histogram */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-sm text-slate-900 uppercase tracking-wider flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-blue-600" />
                Project Risk Score Distribution
              </h3>
              <p className="text-xs text-slate-500">Normalized 0–100 composite risk classification</p>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.risk_distribution} margin={{ top: 10, right: 20, left: -10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#64748b" }} />
                <YAxis tick={{ fontSize: 11, fill: "#64748b" }} />
                <Tooltip
                  formatter={(value: any) => [`${value} projects`, "Count"]}
                  contentStyle={{ backgroundColor: "#0f172a", borderRadius: "8px", border: "none", color: "#fff", fontSize: "12px" }}
                />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {data.risk_distribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* State-Wise Projects & Flagged Count */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-sm text-slate-900 uppercase tracking-wider flex items-center gap-2">
                <MapPin className="w-4 h-4 text-blue-600" />
                Regional Project Density & Flagged Works
              </h3>
              <p className="text-xs text-slate-500">Total works vs priority verification queue by state</p>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data.projects_by_state.slice(0, 8)}
                margin={{ top: 10, right: 20, left: -10, bottom: 25 }}
              >
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="state" tick={{ fontSize: 10, fill: "#64748b" }} interval={0} angle={-20} textAnchor="end" />
                <YAxis tick={{ fontSize: 11, fill: "#64748b" }} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#0f172a", borderRadius: "8px", border: "none", color: "#fff", fontSize: "12px" }}
                />
                <Bar dataKey="total_projects" name="Total Projects" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="high_risk_count" name="High/Critical Risk" fill="#ef4444" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Breakdown */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-sm text-slate-900 uppercase tracking-wider">
                Work Category Breakdown & Peer Allocations
              </h3>
              <p className="text-xs text-slate-500">Distribution across statutory eligible MPLADS project types</p>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data.category_distribution}
                margin={{ top: 10, right: 20, left: -10, bottom: 35 }}
              >
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="category" tick={{ fontSize: 10, fill: "#475569" }} interval={0} angle={-25} textAnchor="end" />
                <YAxis tick={{ fontSize: 11, fill: "#475569" }} />
                <Tooltip
                  formatter={(value: any, name: any) => [
                    name === "count" ? `${value} projects` : `₹ ${(value / 100000).toFixed(1)} Lakhs`,
                    name === "count" ? "Total Works" : "Total Sanction"
                  ]}
                  contentStyle={{ backgroundColor: "#0f172a", borderRadius: "8px", border: "none", color: "#fff", fontSize: "12px" }}
                />
                <Bar dataKey="count" name="Total Works" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
