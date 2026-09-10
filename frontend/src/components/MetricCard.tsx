import React from "react";
import { LucideIcon } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  variant?: "default" | "critical" | "high" | "medium" | "low" | "highlight";
  badgeText?: string;
  onClick?: () => void;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  variant = "default",
  badgeText,
  onClick,
}) => {
  let borderClass = "border-slate-200";
  let iconBg = "bg-slate-100 text-slate-700";
  let valueColor = "text-slate-900";

  if (variant === "critical") {
    borderClass = "border-red-200 bg-red-50/40 hover:border-red-300";
    iconBg = "bg-red-100 text-red-600";
    valueColor = "text-red-700";
  } else if (variant === "high") {
    borderClass = "border-orange-200 bg-orange-50/40 hover:border-orange-300";
    iconBg = "bg-orange-100 text-orange-600";
    valueColor = "text-orange-700";
  } else if (variant === "medium") {
    borderClass = "border-amber-200 bg-amber-50/40 hover:border-amber-300";
    iconBg = "bg-amber-100 text-amber-600";
    valueColor = "text-amber-700";
  } else if (variant === "low") {
    borderClass = "border-emerald-200 bg-emerald-50/40 hover:border-emerald-300";
    iconBg = "bg-emerald-100 text-emerald-600";
    valueColor = "text-emerald-700";
  } else if (variant === "highlight") {
    borderClass = "border-blue-200 bg-blue-50/40 hover:border-blue-300";
    iconBg = "bg-blue-100 text-blue-700";
    valueColor = "text-blue-900";
  }

  return (
    <div
      onClick={onClick}
      className={`rounded-xl border bg-white p-5 shadow-xs transition-all ${borderClass} ${
        onClick ? "cursor-pointer hover:shadow-md hover:-translate-y-0.5" : ""
      }`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            {title}
          </p>
          <p className={`mt-2 text-2xl font-black tracking-tight ${valueColor}`}>
            {value}
          </p>
        </div>
        <div className={`rounded-lg p-2.5 ${iconBg}`}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
      {(subtitle || badgeText) && (
        <div className="mt-3 flex items-center justify-between text-xs">
          {subtitle && <span className="text-slate-500 font-medium">{subtitle}</span>}
          {badgeText && (
            <span className="rounded-full bg-slate-100 px-2 py-0.5 font-semibold text-slate-700">
              {badgeText}
            </span>
          )}
        </div>
      )}
    </div>
  );
};
