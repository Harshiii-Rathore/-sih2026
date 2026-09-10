import React, { useEffect, useRef, useState } from "react";
import L from "leaflet";
import { Filter, Layers, MapPin, Sparkles, ExternalLink, RefreshCw } from "lucide-react";
import { MapMarkerItem } from "../types";
import { fetchMapMarkers } from "../api";

interface MapViewProps {
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

export const MapView: React.FC<MapViewProps> = ({ onSelectProject }) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersLayerRef = useRef<L.LayerGroup | null>(null);

  const [markers, setMarkers] = useState<MapMarkerItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [state, setState] = useState("ALL");
  const [riskLevel, setRiskLevel] = useState("ALL");
  const [category, setCategory] = useState("ALL");
  const [selectedPoint, setSelectedPoint] = useState<MapMarkerItem | null>(null);

  // Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        center: [21.5, 79.5],
        zoom: 5,
        zoomControl: true,
      });

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18,
      }).addTo(map);

      const markersLayer = L.layerGroup().addTo(map);
      markersLayerRef.current = markersLayer;
      mapInstanceRef.current = map;
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Fetch markers from API
  const loadMarkers = () => {
    setLoading(true);
    fetchMapMarkers({ state, riskLevel, category })
      .then((data) => setMarkers(data))
      .catch((err) => console.error("Error fetching map points:", err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadMarkers();
  }, [state, riskLevel, category]);

  // Update Markers on Map
  useEffect(() => {
    if (!mapInstanceRef.current || !markersLayerRef.current) return;

    markersLayerRef.current.clearLayers();

    markers.forEach((p) => {
      let fillColor = "#10b981"; // Low
      if (p.risk_level === "CRITICAL") fillColor = "#ef4444";
      else if (p.risk_level === "HIGH") fillColor = "#f97316";
      else if (p.risk_level === "MEDIUM") fillColor = "#f59e0b";

      const circle = L.circleMarker([p.latitude, p.longitude], {
        radius: p.risk_level === "CRITICAL" ? 8 : 6,
        fillColor: fillColor,
        color: "#ffffff",
        weight: 1.5,
        opacity: 1,
        fillOpacity: 0.85,
      });

      circle.on("click", () => {
        setSelectedPoint(p);
      });

      markersLayerRef.current?.addLayer(circle);
    });
  }, [markers]);

  const formatLakhs = (amt: number) => `₹ ${(amt / 100000).toFixed(1)} L`;

  return (
    <div className="space-y-4 pb-12">
      {/* Map Filter Toolbar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-blue-100 text-blue-700">
            <MapPin className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base font-black text-slate-900 tracking-tight">
              National Geospatial Surveillance Map
            </h1>
            <p className="text-xs text-slate-500">
              Visualizing {markers.length} spatial works across India • Color-coded by AI Risk Severity
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          {/* State */}
          <select
            value={state}
            onChange={(e) => setState(e.target.value)}
            className="py-1.5 px-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 font-semibold focus:outline-none"
          >
            {STATES.map((s) => (
              <option key={s} value={s}>{s === "ALL" ? "All States" : s}</option>
            ))}
          </select>

          {/* Risk Level */}
          <select
            value={riskLevel}
            onChange={(e) => setRiskLevel(e.target.value)}
            className="py-1.5 px-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 font-semibold focus:outline-none"
          >
            <option value="ALL">All Risk Grades</option>
            <option value="CRITICAL">Critical Risk (Red)</option>
            <option value="HIGH">High Risk (Orange)</option>
            <option value="MEDIUM">Medium Risk (Amber)</option>
            <option value="LOW">Low Risk (Green)</option>
          </select>

          {/* Category */}
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="py-1.5 px-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 font-semibold focus:outline-none"
          >
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>{c === "ALL" ? "All Categories" : c}</option>
            ))}
          </select>

          <button
            onClick={loadMarkers}
            className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-600 transition"
            title="Refresh Map Points"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-blue-600" : ""}`} />
          </button>
        </div>
      </div>

      {/* Map & Inspector Container */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Interactive Leaflet Map */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden h-[620px] relative">
          <div ref={mapContainerRef} className="w-full h-full z-10" />

          {/* Map Legend Floating */}
          <div className="absolute bottom-4 left-4 z-20 bg-white/95 backdrop-blur-xs p-3 rounded-xl border border-slate-200 shadow-md text-xs space-y-1.5">
            <span className="font-bold text-[10px] text-slate-400 uppercase tracking-wider block">
              Risk Priority Legend
            </span>
            <div className="flex items-center gap-2 font-medium text-slate-700">
              <span className="w-3 h-3 rounded-full bg-red-600" />
              <span>Critical Risk (80–100)</span>
            </div>
            <div className="flex items-center gap-2 font-medium text-slate-700">
              <span className="w-3 h-3 rounded-full bg-orange-500" />
              <span>High Risk (60–79)</span>
            </div>
            <div className="flex items-center gap-2 font-medium text-slate-700">
              <span className="w-3 h-3 rounded-full bg-amber-500" />
              <span>Medium Risk (30–59)</span>
            </div>
            <div className="flex items-center gap-2 font-medium text-slate-700">
              <span className="w-3 h-3 rounded-full bg-emerald-500" />
              <span>Low Risk (0–29)</span>
            </div>
          </div>
        </div>

        {/* Selected Project Inspection Drawer */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex flex-col h-[620px]">
          <h3 className="font-bold text-sm text-slate-900 uppercase tracking-wider pb-3 border-b border-slate-100 flex items-center gap-2">
            <Layers className="w-4 h-4 text-blue-600" />
            Selected Project Inspector
          </h3>

          {selectedPoint ? (
            <div className="mt-4 space-y-4 flex-1 flex flex-col justify-between overflow-y-auto">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                    {selectedPoint.project_id}
                  </span>
                  <span
                    className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                      selectedPoint.risk_level === "CRITICAL"
                        ? "bg-red-100 text-red-700"
                        : selectedPoint.risk_level === "HIGH"
                        ? "bg-orange-100 text-orange-700"
                        : selectedPoint.risk_level === "MEDIUM"
                        ? "bg-amber-100 text-amber-700"
                        : "bg-emerald-100 text-emerald-700"
                    }`}
                  >
                    Risk: {selectedPoint.risk_score.toFixed(1)}/100
                  </span>
                </div>

                <h4 className="font-black text-base text-slate-900 leading-snug">
                  {selectedPoint.work_title}
                </h4>

                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-1.5">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Category:</span>
                    <span className="font-semibold text-slate-800">{selectedPoint.category}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Location:</span>
                    <span className="font-semibold text-slate-800">{selectedPoint.district}, {selectedPoint.state}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Sanction:</span>
                    <span className="font-bold text-slate-900">{formatLakhs(selectedPoint.sanction_amount)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Status:</span>
                    <span className="font-bold text-blue-600">{selectedPoint.status}</span>
                  </div>
                </div>

                <div className="p-3 bg-red-50/50 rounded-xl border border-red-200 text-xs space-y-1">
                  <span className="font-bold text-red-900 uppercase tracking-wider block text-[10px]">
                    Primary Anomaly Signal:
                  </span>
                  <p className="text-red-950 font-medium leading-relaxed">
                    {selectedPoint.main_anomaly}
                  </p>
                </div>
              </div>

              <button
                onClick={() => onSelectProject(selectedPoint.project_id)}
                className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-sm transition flex items-center justify-center gap-1.5"
              >
                <span>Open Full Investigation Dossier</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-6 text-slate-400">
              <MapPin className="w-10 h-10 mb-2 stroke-[1.5]" />
              <p className="text-xs font-medium text-slate-600">
                Click any marker on the map to inspect project telemetry and anomaly reasons.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
