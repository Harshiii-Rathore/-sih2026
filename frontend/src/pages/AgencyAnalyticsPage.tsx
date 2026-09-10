import React, { useEffect, useState } from "react";
import { Building2, AlertTriangle, ShieldCheck, ExternalLink, X, Coins, FolderKanban } from "lucide-react";
import { AgencyItem } from "../types";
import { fetchAgencies, fetchAgencyProfile } from "../api";
import { RiskBadge } from "../components/RiskBadge";

interface AgencyAnalyticsPageProps {
  onSelectProject: (projectId: string) => void;
}

export const AgencyAnalyticsPage: React.FC<AgencyAnalyticsPageProps> = ({
  onSelectProject,
}) => {
  const [agencies, setAgencies] = useState<AgencyItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAgency, setSelectedAgency] = useState<string | null>(null);
  const [agencyProfile, setAgencyProfile] = useState<{ agency: AgencyItem; projects: any[] } | null>(null);
  const [loadingProfile, setLoadingProfile] = useState(false);

  useEffect(() => {
    fetchAgencies()
      .then((data) => setAgencies(data))
      .catch((err) => console.error("Error fetching agencies:", err))
      .finally(() => setLoading(false));
  }, []);

  const handleOpenAgency = (name: string) => {
    setSelectedAgency(name);
    setLoadingProfile(true);
    fetchAgencyProfile(name)
      .then((data) => setAgencyProfile(data))
      .catch((err) => console.error("Error fetching agency profile:", err))
      .finally(() => setLoadingProfile(false));
  };

  const formatCrores = (amt: number) => `₹ ${(amt / 10000000).toFixed(2)} Cr`;
  const formatLakhs = (amt: number) => `₹ ${(amt / 100000).toFixed(1)} L`;

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-700 text-xs font-bold uppercase tracking-wider">
              Executing Bodies Surveillance
            </span>
            <span className="text-xs text-slate-400 font-medium">Neutral Audit Screening</span>
          </div>
          <h1 className="mt-1 text-2xl font-black text-slate-900 tracking-tight">
            Implementing Agency Performance & Concentration Analytics
          </h1>
          <p className="mt-1 text-sm text-slate-600">
            Monitoring portfolio project values, agency concentration, and execution delays across implementing agencies.
          </p>
        </div>
      </div>

      {/* Agency Ranking Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-50 text-[11px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th className="py-3.5 px-4">Implementing Agency</th>
                <th className="py-3.5 px-4">District / State</th>
                <th className="py-3.5 px-4">Total Works</th>
                <th className="py-3.5 px-4">Total Portfolio Value</th>
                <th className="py-3.5 px-4">Avg Project Value</th>
                <th className="py-3.5 px-4">Priority Verification Works</th>
                <th className="py-3.5 px-4">Risk Proportion</th>
                <th className="py-3.5 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    Loading agency records...
                  </td>
                </tr>
              ) : agencies.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    No agency data available.
                  </td>
                </tr>
              ) : (
                agencies.map((agency) => {
                  const hasAnomaly = agency.risk_percentage >= 20.0 || agency.high_risk_projects_count >= 3;
                  return (
                    <tr
                      key={agency.agency_name}
                      onClick={() => handleOpenAgency(agency.agency_name)}
                      className={`hover:bg-slate-50/80 cursor-pointer transition ${
                        hasAnomaly ? "bg-amber-50/30" : ""
                      }`}
                    >
                      <td className="py-3.5 px-4 font-bold text-slate-900">
                        <div className="flex items-center gap-2">
                          <Building2 className="w-4 h-4 text-slate-400 shrink-0" />
                          <span>{agency.agency_name}</span>
                        </div>
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="font-semibold text-slate-800">{agency.district}</div>
                        <div className="text-[11px] text-slate-400">{agency.state}</div>
                      </td>
                      <td className="py-3.5 px-4 font-mono font-bold text-slate-900">
                        {agency.total_projects}
                      </td>
                      <td className="py-3.5 px-4 font-bold text-slate-900">
                        {formatCrores(agency.total_sanctioned_amount)}
                      </td>
                      <td className="py-3.5 px-4 font-medium text-slate-800">
                        {formatLakhs(agency.average_project_value)}
                      </td>
                      <td className="py-3.5 px-4">
                        {agency.high_risk_projects_count > 0 ? (
                          <span className="inline-flex items-center gap-1 font-bold text-red-600 bg-red-50 border border-red-200 px-2 py-0.5 rounded-full">
                            <AlertTriangle className="w-3 h-3" />
                            {agency.high_risk_projects_count} works
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-emerald-700 font-medium">
                            <ShieldCheck className="w-3.5 h-3.5" />
                            0 works
                          </span>
                        )}
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-slate-200 h-2 rounded-full overflow-hidden">
                            <div
                              className={`h-full ${
                                agency.risk_percentage >= 25 ? "bg-red-500" : "bg-blue-500"
                              }`}
                              style={{ width: `${Math.min(100, agency.risk_percentage)}%` }}
                            />
                          </div>
                          <span className="font-mono font-bold">{agency.risk_percentage}%</span>
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-right whitespace-nowrap">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleOpenAgency(agency.agency_name);
                          }}
                          className="px-2.5 py-1 bg-slate-100 hover:bg-blue-600 hover:text-white rounded-lg font-semibold transition"
                        >
                          View Portfolio
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Agency Portfolio Detail Modal */}
      {selectedAgency && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
          <div className="w-full max-w-4xl max-h-[85vh] rounded-2xl bg-white shadow-2xl border border-slate-200 flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-4 bg-slate-900 text-white border-b border-slate-800">
              <div>
                <h3 className="font-bold text-base text-white">{selectedAgency}</h3>
                <p className="text-xs text-slate-400">Complete execution history and risk score breakdown</p>
              </div>
              <button
                onClick={() => setSelectedAgency(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6 overflow-y-auto space-y-4">
              {loadingProfile || !agencyProfile ? (
                <div className="py-12 text-center text-sm text-slate-500">Loading agency portfolio...</div>
              ) : (
                <>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 bg-slate-50 rounded-xl border border-slate-200 text-xs">
                    <div>
                      <span className="text-slate-500 block">Location:</span>
                      <span className="font-bold text-slate-900">{agencyProfile.agency.district}, {agencyProfile.agency.state}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Total Works:</span>
                      <span className="font-bold text-slate-900">{agencyProfile.agency.total_projects}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Portfolio Budget:</span>
                      <span className="font-bold text-slate-900">{formatCrores(agencyProfile.agency.total_sanctioned_amount)}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Avg Project Size:</span>
                      <span className="font-bold text-slate-900">{formatLakhs(agencyProfile.agency.average_project_value)}</span>
                    </div>
                  </div>

                  <h4 className="font-bold text-xs uppercase tracking-wider text-slate-500 pt-2">
                    Works Executed by {selectedAgency} ({agencyProfile.projects.length})
                  </h4>

                  <div className="divide-y divide-slate-100 border border-slate-200 rounded-xl overflow-hidden text-xs">
                    {agencyProfile.projects.map((p) => (
                      <div
                        key={p.project_id}
                        className="p-3.5 hover:bg-slate-50 flex items-center justify-between gap-4"
                      >
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="font-mono font-bold text-slate-900">{p.project_id}</span>
                            <RiskBadge level={p.risk_level} score={p.risk_score} size="sm" />
                            <span className="text-slate-400">•</span>
                            <span className="text-slate-500">{p.category}</span>
                          </div>
                          <p className="font-semibold text-slate-900">{p.work_title}</p>
                        </div>

                        <div className="flex items-center gap-3 shrink-0">
                          <span className="font-bold text-slate-800">{formatLakhs(p.sanction_amount)}</span>
                          <button
                            onClick={() => {
                              setSelectedAgency(null);
                              onSelectProject(p.project_id);
                            }}
                            className="px-2.5 py-1 rounded bg-blue-600 hover:bg-blue-700 text-white font-semibold flex items-center gap-1"
                          >
                            <span>Inspect</span>
                            <ExternalLink className="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
