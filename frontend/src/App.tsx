import React, { useState } from "react";
import { UserSession } from "./types";
import { Navbar } from "./components/Navbar";
import { AuditLogModal } from "./components/AuditLogModal";
import { LoginPage } from "./pages/LoginPage";
import { DashboardPage } from "./pages/DashboardPage";
import { ProjectMonitoringPage } from "./pages/ProjectMonitoringPage";
import { ProjectDetailPage } from "./pages/ProjectDetailPage";
import { MapView } from "./pages/MapView";
import { AgencyAnalyticsPage } from "./pages/AgencyAnalyticsPage";
import { RealAllocationsPage } from "./pages/RealAllocationsPage";
import { AiPipelinePage } from "./pages/AiPipelinePage";

export const App: React.FC = () => {
  // Pre-seed default session for instant evaluator experience
  const [currentUser, setCurrentUser] = useState<UserSession | null>({
    token: "demo-auditor-token",
    username: "auditor",
    full_name: "Priya Venkatraman",
    role: "Auditor",
    department: "Comptroller & Auditor General Audit Cell",
  });

  const [activeTab, setActiveTab] = useState<string>("dashboard");
  const [selectedProjectId, setSelectedProjectId] = useState<string>("MPL-DEMO-001");
  const [isAuditModalOpen, setIsAuditModalOpen] = useState<boolean>(false);

  // If user logs out
  if (!currentUser) {
    return <LoginPage onLoginSuccess={(session) => setCurrentUser(session)} />;
  }

  const handleSelectProject = (projectId: string) => {
    setSelectedProjectId(projectId);
    setActiveTab("project-detail");
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col font-sans">
      {/* Top Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={(tab) => {
          setActiveTab(tab);
        }}
        currentUser={currentUser}
        setCurrentUser={setCurrentUser}
        openAuditModal={() => setIsAuditModalOpen(true)}
      />

      {/* Main Page View Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        {activeTab === "dashboard" && (
          <DashboardPage
            onSelectProject={handleSelectProject}
            onNavigateToProjects={() => setActiveTab("projects")}
          />
        )}

        {activeTab === "projects" && (
          <ProjectMonitoringPage onSelectProject={handleSelectProject} />
        )}

        {activeTab === "project-detail" && (
          <ProjectDetailPage
            projectId={selectedProjectId}
            onBack={() => setActiveTab("projects")}
            onSelectProject={handleSelectProject}
          />
        )}

        {activeTab === "map" && (
          <MapView onSelectProject={handleSelectProject} />
        )}

        {activeTab === "agencies" && (
          <AgencyAnalyticsPage onSelectProject={handleSelectProject} />
        )}

        {activeTab === "allocations" && <RealAllocationsPage />}

        {activeTab === "pipeline" && <AiPipelinePage />}
      </main>

      {/* Footer */}
      <footer className="bg-slate-900 border-t border-slate-800 text-slate-400 py-6 text-xs mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-200">NIRIKSHAN AI</span>
            <span>• Smart India Hackathon 2026 (SIH26102)</span>
          </div>
          <div className="text-center sm:text-right text-[11px] text-slate-500">
            Ministry of Statistics & Programme Implementation (MoSPI) • Members of Parliament Local Area Development Scheme
          </div>
        </div>
      </footer>

      {/* Audit Log Modal */}
      <AuditLogModal
        isOpen={isAuditModalOpen}
        onClose={() => setIsAuditModalOpen(false)}
      />
    </div>
  );
};

export default App;
