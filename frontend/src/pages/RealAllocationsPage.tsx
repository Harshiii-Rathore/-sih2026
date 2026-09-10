import React, { useEffect, useState } from "react";
import { FileSpreadsheet, Search, CheckCircle2, Building, Layers, Info } from "lucide-react";
import { RealAllocationResponse } from "../types";
import { fetchRealAllocations } from "../api";

export const RealAllocationsPage: React.FC = () => {
  const [data, setData] = useState<RealAllocationResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [stateFilter, setStateFilter] = useState("ALL");
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    setLoading(true);
    fetchRealAllocations(stateFilter)
      .then((res) => setData(res))
      .catch((err) => console.error("Error loading allocations:", err))
      .finally(() => setLoading(false));
  }, [stateFilter]);

  const filteredAllocations = data?.allocations.filter((a) => {
    if (!searchTerm) return true;
    const s = searchTerm.toLowerCase();
    return (
      a.mp_name.toLowerCase().includes(s) ||
      a.constituency.toLowerCase().includes(s) ||
      a.state.toLowerCase().includes(s)
    );
  }) || [];

  const formatCrores = (amt: number) => `₹ ${(amt / 10000000).toFixed(2)} Cr`;
  const formatLakhs = (amt: number) => `₹ ${(amt / 100000).toFixed(2)} Lakhs`;

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
        <div className="flex items-center gap-2">
          <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            OFFICIAL REAL GOVERNMENT DATASET
          </span>
          <span className="text-xs text-slate-400 font-medium">Source: Allocated Limit for Honble MPs.csv</span>
        </div>
        <h1 className="mt-2 text-2xl font-black text-slate-900 tracking-tight">
          Hon'ble Members of Parliament Allocation Limits
        </h1>
        <p className="mt-1 text-sm text-slate-600 max-w-4xl">
          Ingested directly from the Ministry of Statistics & Programme Implementation (MoSPI) allocation records.
          Contains real expenditure limits for all 543 Parliamentary constituencies across India totaling over ₹83,336 Crores.
        </p>

        {/* Data Architecture Reality Disclaimer Box */}
        <div className="mt-4 p-4 rounded-xl bg-blue-50/70 border border-blue-200 flex items-start gap-3 text-xs text-blue-900">
          <Info className="w-5 h-5 text-blue-700 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold uppercase tracking-wider text-[11px]">System Architecture Notice:</span>
            <p className="leading-relaxed">
              This table reflects the <b>real government-allocated limits</b> per Hon'ble MP. Since scheme allocation limits are high-level statutory bounds and do not contain project-level milestone telemetry, NIRIKSHAN AI pairs this real dataset with high-fidelity synthetic demo projects (explicitly marked <code className="bg-blue-100 px-1 py-0.5 rounded font-mono">SYNTHETIC_DEMO</code>) to demonstrate AI-powered anomaly detection on works, timelines, and spatial overlap.
            </p>
          </div>
        </div>
      </div>

      {/* Top Allocation Summary Cards */}
      {data && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="p-5 rounded-2xl border border-slate-200 bg-white shadow-xs">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Total Hon'ble MPs</span>
            <p className="text-2xl font-black text-slate-900 mt-1">{data.total_mps}</p>
            <span className="text-xs text-slate-400">All Lok Sabha Constituencies</span>
          </div>
          <div className="p-5 rounded-2xl border border-slate-200 bg-white shadow-xs">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Total Allocated Limit</span>
            <p className="text-2xl font-black text-blue-900 mt-1 font-mono">{formatCrores(data.total_allocated_limit_inr)}</p>
            <span className="text-xs text-slate-400">Total Approved Financial Cap</span>
          </div>
          <div className="p-5 rounded-2xl border border-slate-200 bg-white shadow-xs">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Average Limit per MP</span>
            <p className="text-2xl font-black text-emerald-800 mt-1 font-mono">
              {formatCrores(data.total_allocated_limit_inr / data.total_mps)}
            </p>
            <span className="text-xs text-slate-400">~₹14.70 to ₹28.14 Cr</span>
          </div>
        </div>
      )}

      {/* State-Wise Allocation Aggregates */}
      {data && data.state_breakdown && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-sm text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <Layers className="w-4 h-4 text-blue-600" />
              State-Wise Allocation Limit Distribution
            </h3>
            <span className="text-xs text-slate-400 font-medium">Aggregated from CSV records</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 text-xs">
            {data.state_breakdown.slice(0, 12).map((sb) => (
              <div
                key={sb.state}
                onClick={() => setStateFilter(sb.state)}
                className={`p-3 rounded-xl border cursor-pointer transition ${
                  stateFilter === sb.state
                    ? "bg-blue-50 border-blue-400 shadow-xs"
                    : "bg-slate-50/70 border-slate-200 hover:border-slate-300"
                }`}
              >
                <div className="font-bold text-slate-900 truncate">{sb.state}</div>
                <div className="flex justify-between items-center mt-1 text-slate-600">
                  <span>{sb.mp_count} MPs</span>
                  <span className="font-bold font-mono text-blue-700">{formatCrores(sb.total_allocated)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* MPs List Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Filter by MP Name, Constituency..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-500 font-medium">Filter by State:</span>
            <select
              value={stateFilter}
              onChange={(e) => setStateFilter(e.target.value)}
              className="py-1.5 px-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 font-semibold focus:outline-none"
            >
              <option value="ALL">All States</option>
              {data?.state_breakdown.map((s) => (
                <option key={s.state} value={s.state}>{s.state}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-50 text-[11px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">Sr No.</th>
                <th className="py-3 px-4">Hon'ble Member of Parliament</th>
                <th className="py-3 px-4">Constituency</th>
                <th className="py-3 px-4">State</th>
                <th className="py-3 px-4 text-right">Allocated Limit (₹)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {loading ? (
                <tr>
                  <td colSpan={5} className="py-12 text-center text-slate-400">
                    Loading MP allocation records...
                  </td>
                </tr>
              ) : filteredAllocations.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-12 text-center text-slate-400">
                    No matching records found.
                  </td>
                </tr>
              ) : (
                filteredAllocations.map((a, idx) => (
                  <tr key={idx} className="hover:bg-slate-50">
                    <td className="py-3 px-4 text-slate-400 font-mono">{a.sr_no || idx + 1}</td>
                    <td className="py-3 px-4 font-bold text-slate-900">{a.mp_name}</td>
                    <td className="py-3 px-4 font-semibold text-blue-700">{a.constituency}</td>
                    <td className="py-3 px-4 text-slate-700">{a.state}</td>
                    <td className="py-3 px-4 text-right font-mono font-bold text-slate-900">
                      ₹ {a.allocated_amount.toLocaleString("en-IN")}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
