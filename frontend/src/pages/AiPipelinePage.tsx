import React, { useState } from "react";
import {
  Cpu,
  Database,
  FileCheck2,
  Sliders,
  AlertCircle,
  Activity,
  Layers,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  ArrowDown
} from "lucide-react";

interface PipelineStep {
  id: string;
  stepNumber: number;
  title: string;
  category: string;
  description: string;
  algorithms: string[];
  formula: string;
  outputs: string[];
}

const PIPELINE_STEPS: PipelineStep[] = [
  {
    id: "ingestion",
    stepNumber: 1,
    title: "Data Sourcing & Ingestion",
    category: "DATA LAYER",
    description: "Decoupled data provider interface supporting real MoSPI allocation limits and high-fidelity project telemetry.",
    algorithms: ["CSV DictReader", "Parameterized SQLite/PostgreSQL Loader", "Schema Normalization"],
    formula: "DataSource \\rightarrow MPLADSDataProvider \\rightarrow EnginePipeline",
    outputs: ["543 Real MP limits", "1,000 Project execution records", "Geospatial coordinate mapping"]
  },
  {
    id: "validation",
    stepNumber: 2,
    title: "Data Integrity & Schema Sanity",
    category: "PRE-PROCESSING",
    description: "Validates field presence, statutory Indian coordinate boundaries, and chronological ordering.",
    algorithms: ["Boundary Verification (lat: 6-38, lon: 68-98)", "ISO Date Parser", "Type Casting"],
    formula: "\\text{Valid}(P) = (\\text{lat},\\text{lon}) \\in \\text{India} \\land \\text{Sanction} > 0",
    outputs: ["Normalized database records", "Initial compliance flags", "Sanitized telemetry"]
  },
  {
    id: "features",
    stepNumber: 3,
    title: "Feature Engineering & Peer Groups",
    category: "STATISTICAL BASELINE",
    description: "Segments projects into statistical peer cohorts by category and geography; derives duration and financial velocity.",
    algorithms: ["Peer Group Clustering", "Category Median & IQR", "Elapsed Months Calculus"],
    formula: "\\text{IQR} = Q_3 - Q_1; \\quad \\Delta_{\\text{cost}} = \\frac{\\text{Cost} - \\text{Median}}{\\text{Median}} \\times 100",
    outputs: ["11 Category benchmarks", "Duration deviations", "Payment concentration indices"]
  },
  {
    id: "rules",
    stepNumber: 4,
    title: "Deterministic Rule Engine",
    category: "COMPLIANCE CHECK",
    description: "Evaluates non-probabilistic statutory rules separate from ML to guarantee regulatory accountability.",
    algorithms: ["Rule 1: Expenditure > Sanction", "Rule 2: Inverted Dates", "Rule 3: Stalled with Zero Spend"],
    formula: "R_{\\text{comp}} = \\sum_{i} w_i \\cdot \\mathbb{I}(\\text{Rule}_i \\text{ breached})",
    outputs: ["Regulatory breach itemization", "Deterministic penalty scores"]
  },
  {
    id: "anomalies",
    stepNumber: 5,
    title: "Multi-Signal Anomaly Detection",
    category: "MACHINE LEARNING",
    description: "Independent multi-dimensional detectors evaluate cost, timeline, and disbursement velocity in parallel.",
    algorithms: ["Cost Anomaly Detector", "Timeline Anomaly Detector", "Expenditure Anomaly Detector"],
    formula: "S_{\\text{cost}}, S_{\\text{time}}, S_{\\text{spend}} \\in [0, 100]",
    outputs: ["Sub-scores per dimension", "Empirical deviation %", "Quantified peer comparisons"]
  },
  {
    id: "overlap",
    stepNumber: 6,
    title: "Potential Spatial & Description Overlap Analysis",
    category: "NLP + GIS",
    description: "Identifies candidate matching works requiring verification using TF-IDF n-gram vectorization and Haversine spatial distance.",
    algorithms: ["TF-IDF Vectorizer (1-2 ngrams)", "Cosine Similarity Matrix", "Haversine Great Circle Formula"],
    formula: "d = 2R \\arcsin \\sqrt{\\sin^2 \\frac{\\Delta \\phi}{2} + \\cos \\phi_1 \\cos \\phi_2 \\sin^2 \\frac{\\Delta \\lambda}{2}}; \\quad \\text{Sim} = \\frac{u \\cdot v}{\\|u\\| \\|v\\|}",
    outputs: ["Candidate similar works list", "Spatial distance (km)", "Text similarity %"]
  },
  {
    id: "scoring",
    stepNumber: 7,
    title: "Configurable Weighted Risk Scoring",
    category: "SYNTHESIS",
    description: "Fuses all normalized signals into an auditable 0–100 overall score using transparent configurable weights.",
    algorithms: ["Weighted Multi-Criteria Synthesis", "Risk Tier Classification (Low/Med/High/Critical)"],
    formula: "\\text{Risk} = 0.25 C + 0.20 T + 0.20 O + 0.15 E + 0.10 A + 0.10 R_{\\text{comp}}",
    outputs: ["Overall Risk Score (0-100)", "Risk Classification (Critical/High/Med/Low)"]
  },
  {
    id: "xai",
    stepNumber: 8,
    title: "Explainable AI (XAI) Generation",
    category: "EXPLAINABILITY",
    description: "Generates clear, human-understandable audit rationales highlighting exactly WHY the project was prioritized.",
    algorithms: ["Factor Ranking Engine", "Quantified Evidence Assembler", "Natural Language Synthesizer"],
    formula: "\\text{Evidence} = \\{ \\text{Cost Dev: } +104\\%, \\text{ Delay: } +83\\%, \\text{ Overlap: } 0.7\\text{km} \\}",
    outputs: ["Why was this flagged? cards", "Itemized evidentiary metrics", "Audit briefs"]
  },
  {
    id: "priority",
    stepNumber: 9,
    title: "Investigation Priority Queue",
    category: "DECISION SUPPORT",
    description: "Delivers prioritized workflows to field officers with actionable recommended verification steps.",
    algorithms: ["Prioritized Triage Queue", "ReportLab PDF Dossier Generator"],
    formula: "\\text{Queue} = \\text{Sort}(\\text{Projects}, \\text{by}=\\text{Risk Score}, \\text{desc})",
    outputs: ["Investigation Dossier (PDF)", "Triage Action Protocol"]
  }
];

export const AiPipelinePage: React.FC = () => {
  const [selectedStep, setSelectedStep] = useState<PipelineStep>(PIPELINE_STEPS[6]); // Default to Scoring

  return (
    <div className="space-y-6 pb-16">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
        <div className="flex items-center gap-2">
          <span className="px-2.5 py-0.5 rounded-full bg-indigo-100 text-indigo-800 text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-indigo-600" />
            AI ARCHITECTURE & METHODOLOGY
          </span>
          <span className="text-xs text-slate-400 font-medium">SIH 2026 Technical Presentation Reference</span>
        </div>
        <h1 className="mt-2 text-2xl font-black text-slate-900 tracking-tight">
          NIRIKSHAN AI Risk Engine Pipeline
        </h1>
        <p className="mt-1 text-sm text-slate-600 max-w-4xl">
          An explainable, multi-signal early-warning architecture designed to triage MPLADS projects for auditor verification.
          Built on deterministic rules, robust statistical benchmarks, TF-IDF NLP similarity, and GIS Haversine calculations.
        </p>

        <div className="mt-4 p-3 bg-slate-900 text-white rounded-xl flex items-center justify-between text-xs">
          <div className="flex items-center gap-2 font-medium">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Core Ethical Principle: <b>"We don't replace auditors. We help them know where to look first."</b></span>
          </div>
          <span className="text-slate-400 font-mono text-[11px]">Zero Unexplainable Black-Box ML</span>
        </div>
      </div>

      {/* Interactive Pipeline Visual Diagram */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Step Cards Flow */}
        <div className="lg:col-span-2 space-y-3">
          {PIPELINE_STEPS.map((step, idx) => {
            const isSelected = selectedStep.id === step.id;
            return (
              <div key={step.id}>
                <div
                  onClick={() => setSelectedStep(step)}
                  className={`p-4 rounded-xl border cursor-pointer transition flex items-center justify-between gap-4 ${
                    isSelected
                      ? "bg-blue-50 border-blue-500 shadow-md ring-1 ring-blue-500"
                      : "bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50/80"
                  }`}
                >
                  <div className="flex items-center gap-3.5">
                    <span
                      className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs shrink-0 ${
                        isSelected ? "bg-blue-600 text-white" : "bg-slate-100 text-slate-700"
                      }`}
                    >
                      0{step.stepNumber}
                    </span>
                    <div>
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                        {step.category}
                      </span>
                      <h3 className="font-bold text-sm text-slate-900">{step.title}</h3>
                    </div>
                  </div>

                  <div className="text-right hidden sm:block">
                    <span className="text-xs text-blue-600 font-semibold hover:underline">
                      Inspect Specs &rarr;
                    </span>
                  </div>
                </div>

                {idx < PIPELINE_STEPS.length - 1 && (
                  <div className="flex justify-center py-1">
                    <ArrowDown className="w-3.5 h-3.5 text-slate-300" />
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Right Col: Deep-Dive Inspector for Selected Step */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs h-fit sticky top-24 space-y-5">
          <div className="border-b border-slate-100 pb-3">
            <span className="text-[10px] font-bold text-blue-600 uppercase tracking-wider block">
              Stage 0{selectedStep.stepNumber} • {selectedStep.category}
            </span>
            <h2 className="text-lg font-black text-slate-900 tracking-tight mt-1">
              {selectedStep.title}
            </h2>
          </div>

          <div className="space-y-2">
            <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider">Functional Role</h4>
            <p className="text-xs text-slate-700 leading-relaxed font-medium">
              {selectedStep.description}
            </p>
          </div>

          <div className="space-y-2">
            <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider">Algorithmic Formulation</h4>
            <div className="p-3 bg-slate-900 text-emerald-400 rounded-xl font-mono text-xs overflow-x-auto">
              {selectedStep.formula}
            </div>
          </div>

          <div className="space-y-2">
            <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider">Methods / Algorithms</h4>
            <div className="space-y-1">
              {selectedStep.algorithms.map((alg, i) => (
                <div key={i} className="flex items-center gap-2 text-xs text-slate-700">
                  <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                  <span>{alg}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-2 pt-2 border-t border-slate-100">
            <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider">Pipeline Outputs</h4>
            <div className="space-y-1">
              {selectedStep.outputs.map((out, i) => (
                <div key={i} className="flex items-center gap-2 text-xs text-slate-600">
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-400" />
                  <span>{out}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Configurable Risk Weights Box */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-2">
            <span className="font-bold text-slate-900 uppercase tracking-wider block text-[10px]">
              Engine Weight Configuration:
            </span>
            <div className="grid grid-cols-2 gap-1 text-[11px] text-slate-600">
              <div>Cost Anomaly: <b>25%</b></div>
              <div>Timeline Delay: <b>20%</b></div>
              <div>Spatial Overlap: <b>20%</b></div>
              <div>Expenditure: <b>15%</b></div>
              <div>Agency Pattern: <b>10%</b></div>
              <div>Compliance: <b>10%</b></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
