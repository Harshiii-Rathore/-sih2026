import React from "react";

interface RiskBadgeProps {
  level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL" | string;
  score?: number;
  size?: "sm" | "md" | "lg";
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, score, size = "md" }) => {
  const normLevel = (level || "LOW").toUpperCase();

  let colorClasses = "bg-emerald-50 text-emerald-700 border-emerald-200";
  let dotColor = "bg-emerald-500";
  let label = "Low Risk";

  if (normLevel === "CRITICAL") {
    colorClasses = "bg-red-50 text-red-700 border-red-200 ring-1 ring-red-300";
    dotColor = "bg-red-600 animate-pulse";
    label = "Critical Risk";
  } else if (normLevel === "HIGH") {
    colorClasses = "bg-orange-50 text-orange-700 border-orange-200";
    dotColor = "bg-orange-500";
    label = "High Risk";
  } else if (normLevel === "MEDIUM") {
    colorClasses = "bg-amber-50 text-amber-700 border-amber-200";
    dotColor = "bg-amber-500";
    label = "Medium Risk";
  }

  const sizeClasses =
    size === "sm"
      ? "text-xs px-2 py-0.5 gap-1.5"
      : size === "lg"
      ? "text-sm px-3.5 py-1.5 gap-2 font-semibold"
      : "text-xs px-2.5 py-1 gap-1.5 font-medium";

  return (
    <span
      className={`inline-flex items-center rounded-full border ${colorClasses} ${sizeClasses} transition-all`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${dotColor}`} />
      <span>{label}</span>
      {score !== undefined && (
        <span className="font-mono font-bold opacity-90">({score.toFixed(0)})</span>
      )}
    </span>
  );
};
