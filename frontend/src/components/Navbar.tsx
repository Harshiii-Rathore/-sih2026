import React from "react";
import {
  ShieldAlert,
  LayoutDashboard,
  FolderKanban,
  MapPin,
  Building2,
  FileSpreadsheet,
  Cpu,
  History,
  UserCheck
} from "lucide-react";
import { UserSession } from "../types";

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  currentUser: UserSession;
  setCurrentUser: (user: UserSession) => void;
  openAuditModal: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  currentUser,
  setCurrentUser,
  openAuditModal,
}) => {
  const switchRole = (role: string) => {
    if (role === "Auditor") {
      setCurrentUser({
        token: "demo-auditor-token",
        username: "auditor",
        full_name: "Priya Venkatraman",
        role: "Auditor",
        department: "CAG Audit Cell"
      });
    } else if (role === "Monitoring Officer") {
      setCurrentUser({
        token: "demo-officer-token",
        username: "officer",
        full_name: "Rajesh Kumar Sharma",
        role: "Monitoring Officer",
        department: "MoSPI MPLADS Division"
      });
    } else {
      setCurrentUser({
        token: "demo-admin-token",
        username: "admin",
        full_name: "Sanjay Singhal",
        role: "Administrator",
        department: "MoSPI National Data Centre"
      });
    }
  };

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "projects", label: "Project Monitoring", icon: FolderKanban },
    { id: "map", label: "Geospatial Map", icon: MapPin },
    { id: "agencies", label: "Agency Analytics", icon: Building2 },
    { id: "allocations", label: "Real MP Limits", icon: FileSpreadsheet },
    { id: "pipeline", label: "AI Risk Engine", icon: Cpu },
  ];

  return (
    <header className="sticky top-0 z-40 bg-slate-900 border-b border-slate-800 text-white shadow-md">
      {/* Top Ministry Ribbon */}
      <div className="bg-slate-950 px-6 py-1.5 border-b border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 font-medium tracking-wide text-slate-300">
            <span className="inline-block w-2.5 h-1.5 bg-amber-500 rounded-sm" />
            <span className="inline-block w-2.5 h-1.5 bg-white rounded-sm" />
            <span className="inline-block w-2.5 h-1.5 bg-emerald-600 rounded-sm" />
            <span>GOVERNMENT OF INDIA • MINISTRY OF STATISTICS & PROGRAMME IMPLEMENTATION (MoSPI)</span>
          </div>
          <span className="text-slate-600">•</span>
          <span>SIH 2026 Problem Statement: SIH26102</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-blue-950/80 text-blue-300 border border-blue-800/60 font-mono text-[11px]">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
            SYNTHETIC DEMO DATASET • 543 REAL MP LIMITS INGESTED
          </span>
        </div>
      </div>

      {/* Main Navigation Bar */}
      <div className="px-6 py-3 flex items-center justify-between">
        {/* Logo & Platform Name */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab("dashboard")}>
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center shadow-lg shadow-blue-500/20 border border-blue-400/30">
            <ShieldAlert className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-lg tracking-wider text-white">NIRIKSHAN</span>
              <span className="text-xs px-1.5 py-0.5 rounded font-bold bg-blue-500/20 text-blue-400 border border-blue-400/30 tracking-widest">
                AI
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium tracking-wide">
              MPLADS Early-Warning & Decision Support System
            </p>
          </div>
        </div>

        {/* Center Nav Links */}
        <nav className="flex items-center gap-1 bg-slate-800/60 p-1 rounded-lg border border-slate-700/60">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  isActive
                    ? "bg-blue-600 text-white shadow-sm shadow-blue-600/30 font-semibold"
                    : "text-slate-300 hover:text-white hover:bg-slate-700/60"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Right Action Tools: Audit Log & Role Selector */}
        <div className="flex items-center gap-3">
          <button
            onClick={openAuditModal}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 border border-slate-700 transition"
            title="View Official Audit Trail"
          >
            <History className="w-3.5 h-3.5 text-blue-400" />
            <span>Audit Trail</span>
          </button>

          {/* User / Role Dropdown Simulation */}
          <div className="flex items-center gap-2 pl-2 border-l border-slate-800">
            <div className="w-7 h-7 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-blue-400">
              <UserCheck className="w-4 h-4" />
            </div>
            <div className="text-left text-xs">
              <div className="text-slate-200 font-medium leading-none">{currentUser.full_name}</div>
              <div className="text-[10px] text-slate-400 flex items-center gap-1 mt-0.5">
                <span className="text-blue-400 font-semibold">{currentUser.role}</span>
                <span>•</span>
                <select
                  value={currentUser.role}
                  onChange={(e) => switchRole(e.target.value)}
                  className="bg-transparent text-slate-400 text-[10px] focus:outline-none cursor-pointer underline hover:text-blue-300"
                >
                  <option value="Auditor" className="bg-slate-900 text-white">Switch to Auditor</option>
                  <option value="Monitoring Officer" className="bg-slate-900 text-white">Switch to Officer</option>
                  <option value="Administrator" className="bg-slate-900 text-white">Switch to Admin</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
