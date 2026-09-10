import React, { useEffect, useState } from "react";
import { X, History, User, Clock, Shield } from "lucide-react";
import { AuditLogItem } from "../types";
import { fetchAuditLogs } from "../api";

interface AuditLogModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AuditLogModal: React.FC<AuditLogModalProps> = ({ isOpen, onClose }) => {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      fetchAuditLogs()
        .then((data) => setLogs(data))
        .catch((err) => console.error("Audit log error:", err))
        .finally(() => setLoading(false));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
      <div className="w-full max-w-3xl max-h-[85vh] rounded-2xl bg-white shadow-2xl border border-slate-200 flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 bg-slate-900 text-white border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-blue-600/30 text-blue-400 border border-blue-500/30">
              <History className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-base text-white">Official System Audit Trail</h3>
              <p className="text-xs text-slate-400">Immutable chronological record of monitoring actions and report requests</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto divide-y divide-slate-100 flex-1">
          {loading ? (
            <div className="py-12 text-center text-sm text-slate-500">Loading audit history...</div>
          ) : logs.length === 0 ? (
            <div className="py-12 text-center text-sm text-slate-500">No actions recorded yet.</div>
          ) : (
            logs.map((log) => (
              <div key={log.id} className="py-3.5 first:pt-0 last:pb-0 flex items-start gap-4">
                <div className="mt-1 p-2 rounded-full bg-blue-50 text-blue-600 border border-blue-200 shrink-0">
                  <Shield className="w-3.5 h-3.5" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-bold text-slate-900">{log.action}</p>
                    <span className="flex items-center gap-1 text-[11px] text-slate-400 font-mono">
                      <Clock className="w-3 h-3" />
                      {log.timestamp}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 mt-1 text-xs text-slate-600">
                    <span className="inline-flex items-center gap-1 font-medium text-slate-800">
                      <User className="w-3 h-3 text-slate-400" />
                      {log.user_name}
                    </span>
                    <span className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 text-[10px] font-semibold">
                      {log.user_role}
                    </span>
                    {log.project_id && (
                      <span className="font-mono text-blue-600 font-semibold bg-blue-50 px-1.5 py-0.5 rounded text-[11px]">
                        {log.project_id}
                      </span>
                    )}
                  </div>
                  {log.details && (
                    <p className="mt-1 text-xs text-slate-500 font-sans">{log.details}</p>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500">
          <span>Compliant with Statutory Government Audit Logging Guidelines</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-800 hover:bg-slate-900 text-white rounded-lg font-medium transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
