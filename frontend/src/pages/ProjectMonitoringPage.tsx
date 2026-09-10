import React, { useEffect, useState } from "react";
import {
  Search,
  Filter,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  RefreshCw,
  AlertCircle
} from "lucide-react";
import { ProjectItem } from "../types";
import { fetchProjects } from "../api";
import { RiskBadge } from "../components/RiskBadge";

interface ProjectMonitoringPageProps {
  onSelectProject: (projectId: string) => void;
}

const STATES = [
  "ALL",
  "Maharashtra",
  "Uttar Pradesh",
  "Tamil Nadu",
  "Bihar",
  "Karnataka",
  "Rajasthan",
  "Gujarat",
  "West Bengal",
  "Kerala",
  "Madhya Pradesh",
  "Odisha",
  "Delhi",
];

const CATEGORIES = [
  "ALL",
  "Community Halls",
  "Roads",
  "Drinking Water",
  "Sanitation",
  "Education",
  "Healthcare",
  "Street Lighting",
  "Drainage",
  "Public Utilities",
  "Sports Facilities",
  "Public Infrastructure",
];

export const ProjectMonitoringPage: React.FC<ProjectMonitoringPageProps> = ({
  onSelectProject,
}) => {
  const [projects, setProjects] = useState<ProjectItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Filters & Sorting state
  const [search, setSearch] = useState("");
  const [state, setState] = useState("ALL");
  const [category, setCategory] = useState("ALL");
  const [riskLevel, setRiskLevel] = useState("ALL");
  const [status, setStatus] = useState("ALL");
  const [sortBy, setSortBy] = useState("risk_score");
  const [sortDir, setSortDir] = useState("desc");

  const loadData = () => {
    setLoading(true);
    fetchProjects({
      page,
      pageSize: 15,
      search,
      state,
      category,
      riskLevel,
      status,
      sortBy,
      sortDir,
    })
      .then((res) => {
        setProjects(res.items);
        setTotal(res.total);
        setTotalPages(res.totalPages);
      })
      .catch((err) => console.error("Error loading projects:", err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, [page, state, category, riskLevel, status, sortBy, sortDir]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadData();
  };

  const toggleSort = (col: string) => {
    if (sortBy === col) {
      setSortDir(sortDir === "desc" ? "asc" : "desc");
    } else {
      setSortBy(col);
      setSortDir("desc");
    }
  };

  const formatLakhs = (amt: number) => `₹ ${(amt / 100000).toFixed(1)} L`;

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-700 text-xs font-bold uppercase tracking-wider">
              Surveillance Grid
            </span>
            <span className="text-xs text-slate-400 font-medium">Default sort: Highest Risk First</span>
          </div>
          <h1 className="mt-1 text-2xl font-black text-slate-900 tracking-tight">
            MPLADS Project Monitoring & Audit Prioritization
          </h1>
          <p className="mt-1 text-sm text-slate-600">
            Showing {total.toLocaleString()} monitored works. Every project evaluated across cost, timeline, spatial overlap, and compliance.
          </p>
        </div>

        <button
          onClick={() => { setPage(1); loadData(); }}
          className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold transition self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-blue-600" : ""}`} />
          <span>Refresh Records</span>
        </button>
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs space-y-3">
        {/* Search Input */}
        <form onSubmit={handleSearchSubmit} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by Title, Project ID (e.g. MPL-DEMO-001), District, MP, or Implementing Agency..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition"
            />
          </div>
          <button
            type="submit"
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold transition shadow-xs"
          >
            Search
          </button>
        </form>

        {/* Filter Dropdowns */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1 border-t border-slate-100 text-xs">
          {/* State */}
          <div>
            <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">State</label>
            <select
              value={state}
              onChange={(e) => { setState(e.target.value); setPage(1); }}
              className="w-full py-1.5 px-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 font-medium focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              {STATES.map((s) => (
                <option key={s} value={s}>{s === "ALL" ? "All States" : s}</option>
              ))}
            </select>
          </div>

          {/* Risk Level */}
          <div>
            <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Risk Severity</label>
            <select
              value={riskLevel}
              onChange={(e) => { setRiskLevel(e.target.value); setPage(1); }}
              className="w-full py-1.5 px-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 font-medium focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="ALL">All Risk Levels</option>
              <option value="CRITICAL">Critical (Score 80–100)</option>
              <option value="HIGH">High (Score 60–79)</option>
              <option value="MEDIUM">Medium (Score 30–59)</option>
              <option value="LOW">Low (Score 0–29)</option>
            </select>
          </div>

          {/* Category */}
          <div>
            <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Work Category</label>
            <select
              value={category}
              onChange={(e) => { setCategory(e.target.value); setPage(1); }}
              className="w-full py-1.5 px-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 font-medium focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>{c === "ALL" ? "All Categories" : c}</option>
              ))}
            </select>
          </div>

          {/* Status */}
          <div>
            <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Execution Status</label>
            <select
              value={status}
              onChange={(e) => { setStatus(e.target.value); setPage(1); }}
              className="w-full py-1.5 px-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 font-medium focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="ALL">All Statuses</option>
              <option value="DELAYED">Delayed</option>
              <option value="STALLED">Stalled</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="COMPLETED">Completed</option>
              <option value="SANCTIONED">Sanctioned</option>
            </select>
          </div>
        </div>
      </div>

      {/* Projects Data Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-50/80 text-[11px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th
                  onClick={() => toggleSort("risk_score")}
                  className="py-3.5 px-4 cursor-pointer hover:text-slate-900 transition"
                >
                  <div className="flex items-center gap-1.5">
                    <span>Risk Priority</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-400" />
                  </div>
                </th>
                <th className="py-3.5 px-4">Project ID</th>
                <th className="py-3.5 px-4">Location</th>
                <th className="py-3.5 px-4">Work Description</th>
                <th
                  onClick={() => toggleSort("sanction_amount")}
                  className="py-3.5 px-4 cursor-pointer hover:text-slate-900 transition"
                >
                  <div className="flex items-center gap-1.5">
                    <span>Sanction / Spend</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-400" />
                  </div>
                </th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4">Primary Anomaly Signal</th>
                <th className="py-3.5 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    <div className="flex items-center justify-center gap-2">
                      <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                      <span>Loading records...</span>
                    </div>
                  </td>
                </tr>
              ) : projects.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    No matching projects found for current filter criteria.
                  </td>
                </tr>
              ) : (
                projects.map((p) => {
                  const isFlagship = p.project_id === "MPL-DEMO-001";
                  return (
                    <tr
                      key={p.project_id}
                      onClick={() => onSelectProject(p.project_id)}
                      className={`hover:bg-slate-50/80 cursor-pointer transition ${
                        isFlagship ? "bg-red-50/30 font-medium" : ""
                      }`}
                    >
                      <td className="py-3 px-4 whitespace-nowrap">
                        <RiskBadge level={p.risk_level} score={p.risk_score} size="sm" />
                      </td>
                      <td className="py-3 px-4 font-mono font-bold text-slate-900 whitespace-nowrap">
                        <div className="flex items-center gap-1.5">
                          <span>{p.project_id}</span>
                          {isFlagship && (
                            <span className="px-1.5 py-0.2 bg-red-600 text-white rounded text-[9px] font-black uppercase">
                              Demo Case
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <div className="font-semibold text-slate-900">{p.district}</div>
                        <div className="text-[11px] text-slate-400">{p.state}</div>
                      </td>
                      <td className="py-3 px-4 max-w-xs">
                        <div className="font-semibold text-slate-900 line-clamp-1">{p.work_title}</div>
                        <div className="text-[11px] text-blue-600 font-medium">{p.work_category}</div>
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <div className="font-bold text-slate-900">{formatLakhs(p.sanction_amount)}</div>
                        <div className="text-[11px] text-slate-400">Spent: {formatLakhs(p.expenditure_amount)}</div>
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider ${
                            p.status === "COMPLETED"
                              ? "bg-emerald-100 text-emerald-800"
                              : p.status === "DELAYED"
                              ? "bg-red-100 text-red-800 font-black"
                              : p.status === "STALLED"
                              ? "bg-purple-100 text-purple-800 font-black"
                              : "bg-blue-100 text-blue-800"
                          }`}
                        >
                          {p.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 max-w-sm">
                        <div className="text-xs text-slate-700 line-clamp-2 leading-tight">
                          {p.top_factor}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-right whitespace-nowrap">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectProject(p.project_id);
                          }}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-blue-600 hover:text-white text-slate-700 text-xs font-semibold transition"
                        >
                          <span>Inspect</span>
                          <ExternalLink className="w-3 h-3" />
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="px-6 py-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs text-slate-600">
          <div>
            Showing Page <span className="font-bold text-slate-900">{page}</span> of{" "}
            <span className="font-bold text-slate-900">{totalPages}</span> (Total {total} works)
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="p-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed transition"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="font-mono px-2 font-bold">{page}</span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="p-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed transition"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
