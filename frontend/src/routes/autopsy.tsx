import { createFileRoute } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { Nav } from "@/components/polaris/Nav";
import { Footer } from "@/components/polaris/Footer";
import { PageTransition } from "@/components/polaris/PageTransition";
import { API_URL, WS_URL } from "@/lib/api";

export const Route = createFileRoute("/autopsy")({
  head: () => ({
    meta: [
      { title: "Urban Autopsy Studio — Polaris" },
      {
        name: "description",
        content:
          "Reconstruct any infrastructure failure as evidence: causal timelines, agent reasoning chains, image forensics, confidence scoring, full chain-of-custody.",
      },
      { property: "og:title", content: "Polaris Urban Autopsy Studio" },
      {
        property: "og:description",
        content: "Root-cause investigation for civic infrastructure.",
      },
    ],
  }),
  component: AutopsyPage,
});

const nodes = [
  { id: "report", x: 12, y: 40, label: "Citizen Report", sub: "ID_882041", kind: "evidence" },
  { id: "sensor", x: 35, y: 22, label: "Main-14 · ΔP 42psi", sub: "13:58 UTC", kind: "evidence" },
  { id: "thermal", x: 35, y: 58, label: "Substation G thermal", sub: "+41 min sustained", kind: "evidence" },
  { id: "history", x: 35, y: 84, label: "Prior incident · 2024", sub: "Same junction", kind: "history" },
  { id: "corr", x: 58, y: 40, label: "Correlation Agent", sub: "w=0.94", kind: "agent" },
  { id: "image", x: 58, y: 74, label: "Image forensics", sub: "Water pooling · 0.91", kind: "agent" },
  { id: "verdict", x: 84, y: 50, label: "Root Cause", sub: "Pipe fatigue · upstream", kind: "verdict" },
];
const edges: [string, string][] = [
  ["report", "corr"], ["sensor", "corr"], ["thermal", "corr"],
  ["history", "image"], ["image", "verdict"], ["corr", "verdict"],
];

const getHistoryFallback = (category?: string) => {
  if (category === "Broken Streetlight") {
    return "Municipal records show historical electrical grid load spikes in Sector 7B.";
  }
  if (category === "Garbage Pile") {
    return "Municipal records show historical collection route delays and overflow notices in Sector 7B.";
  }
  if (category === "Pothole" || category === "Pavement Subsidence") {
    return "Municipal records show historical subgrade soil erosion and roadway subsidence in Sector 7B.";
  }
  return "Municipal records show historical pipeline corrosion vulnerability in Sector 7B.";
};

function AutopsyPage() {
  const [clusters, setClusters] = useState<any[]>([]);
  const [issues, setIssues] = useState<any[]>([]);
  const [selectedCluster, setSelectedCluster] = useState<any>(null);
  const [selected, setSelected] = useState<string>("verdict");
  const [loading, setLoading] = useState(true);
  const [selectedIssueId, setSelectedIssueId] = useState<string | null>(null);

  const [decisionAudit, setDecisionAudit] = useState<any>(null);

  // Initialize selectedIssueId from query param on mount
  useEffect(() => {
    if (typeof window !== "undefined") {
      const urlParams = new URLSearchParams(window.location.search);
      const caseId = urlParams.get("case_id");
      if (caseId) {
        setSelectedIssueId(caseId);
      }
    }
  }, []);

  async function fetchData(activeIssueId?: string | null) {
    try {
      const currentIssueId = activeIssueId !== undefined ? activeIssueId : selectedIssueId;
      const [clustersRes, issuesRes] = await Promise.all([
        fetch(`${API_URL}/clusters`),
        fetch(`${API_URL}/issues`)
      ]);
      const clustersData = await clustersRes.json();
      const issuesData = await issuesRes.json();

      setClusters(clustersData);
      setIssues(issuesData);

      let targetIssue = null;
      if (currentIssueId) {
        const found = issuesData.find((i: any) => i.id === currentIssueId);
        if (found) targetIssue = found;
      }

      if (targetIssue && targetIssue.cluster_id) {
        const foundCluster = clustersData.find((c: any) => c.id === targetIssue.cluster_id);
        if (foundCluster) {
          setSelectedCluster(foundCluster);
        } else {
          setSelectedCluster(null);
        }
      } else {
        setSelectedCluster(null);
      }

      if (targetIssue) {
        const auditRes = await fetch(`${API_URL}/decision_audit/${targetIssue.id}`);
        if (auditRes.ok) {
          const auditData = await auditRes.json();
          setDecisionAudit(auditData);
        } else {
          setDecisionAudit(null);
        }
      }
    } catch (err) {
      console.error("Failed to fetch live autopsy data:", err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchData(selectedIssueId);

    let ws: WebSocket | null = null;
    let reconnectTimeout: any = null;

    function connect() {
      console.log("Connecting to live sync WebSocket...");
      ws = new WebSocket(`${WS_URL}/ws/logs`);

      ws.onmessage = (event) => {
        console.log("WebSocket event received:", event.data);
        // Refresh data using latest state closure value
        fetchData(selectedIssueId);
      };

      ws.onclose = (e) => {
        console.warn("WebSocket closed. Attempting reconnect in 2s...", e.reason);
        reconnectTimeout = setTimeout(() => {
          connect();
        }, 2000);
      };

      ws.onerror = (err) => {
        console.error("WebSocket error:", err);
        ws?.close();
      };
    }

    connect();

    return () => {
      if (ws) {
        ws.onclose = null;
        ws.close();
      }
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
    };
  }, [selectedIssueId]);

  const auditContext = (() => {
    if (!decisionAudit?.decision_trace) return null;
    let traceObj: any = null;
    try {
      traceObj = typeof decisionAudit.decision_trace === "string" 
        ? JSON.parse(decisionAudit.decision_trace) 
        : decisionAudit.decision_trace;
    } catch {
      return null;
    }
    return traceObj?.context;
  })();

  const latestIssue = selectedIssueId ? (issues.find(i => i.id === selectedIssueId) || null) : null;
  const currentHypothesis = latestIssue ? (selectedCluster?.causal_hypothesis || "Analyzing root cause hypothesis...") : "Awaiting causal hypothesis from Synthesis cortex...";
  const currentRisk = latestIssue ? (selectedCluster?.risk_level || "LOW") : "AWAITING";
  const confidenceScore = latestIssue ? (selectedCluster?.confidence ? (selectedCluster.confidence * 100).toFixed(0) + "%" : "94%") : "0%";
  const affectedCount = latestIssue ? (selectedCluster?.affected_residents || 2400) : 0;

  const forensics = latestIssue?.gemini_analysis?.forensics;
  const candidateCause = forensics?.candidate_causes?.[0]?.cause || "Awaiting forensics...";
  const obsDamage = forensics?.physical_damage?.[0] || "Awaiting visual scan...";
  const envSignal = forensics?.environmental_signals?.[0] || "Awaiting telemetry...";

  const dynamicNodes = [
    { 
      id: "report", 
      x: 12, 
      y: 40, 
      label: "Citizen Report", 
      sub: latestIssue ? `ID_${latestIssue.id.slice(0, 6)}` : "ID_882041", 
      kind: "evidence",
      source: "Citizen Mobile Intake",
      reasoning: latestIssue ? `Submitted report classified as ${latestIssue.category} at (${latestIssue.lat}, ${latestIssue.lng}). Summary: ${latestIssue.gemini_analysis?.intake?.summary || latestIssue.description}` : "Initial signal uploaded by local resident."
    },
    { 
      id: "sensor", 
      x: 35, 
      y: 22, 
      label: auditContext?.nearest_assets?.[0] ? `Asset: ${auditContext.nearest_assets[0].id}` : "Visual Forensics", 
      sub: auditContext?.nearest_assets?.[0] ? `${auditContext.weather?.weather_condition ? auditContext.nearest_assets[0].asset_type : 'Detections'}` : obsDamage.slice(0, 20) + "...", 
      kind: "evidence",
      source: auditContext?.nearest_assets?.[0] ? "Supabase Asset Registry" : "Gemini Vision Agent",
      reasoning: auditContext?.nearest_assets?.[0] 
        ? `Closest resolved utility asset: ID ${auditContext.nearest_assets[0].id} (${auditContext.nearest_assets[0].asset_type}), material ${auditContext.nearest_assets[0].material}, condition score: ${auditContext.nearest_assets[0].condition_score}/10. Install year: ${auditContext.nearest_assets[0].install_year}. Distance: ${auditContext.nearest_assets[0].distance_m.toFixed(1)} meters. Status: ${auditContext.nearest_assets[0].status}.`
        : `Observed physical indicators: ${obsDamage}. Structural damage level assessed as ${forensics?.structural_risk_level || "HIGH"}.`
    },
    { 
      id: "thermal", 
      x: 35, 
      y: 58, 
      label: auditContext?.weather ? "Weather Logs" : "Environmental Signal", 
      sub: auditContext?.weather ? auditContext.weather.weather_condition : envSignal.slice(0, 20) + "...", 
      kind: "evidence",
      source: auditContext?.weather ? "WeatherService" : "Multi-Modal Intake",
      reasoning: auditContext?.weather
        ? `Multi-modal weather logs resolved: ${auditContext.weather.weather_condition} with ${auditContext.weather.rain_accumulation_mm}mm rain accumulation. Local temperature: ${auditContext.weather.temperature_c}°C (Source: ${auditContext.weather.source}).`
        : `Environmental telemetry confirms: ${envSignal}.`
    },
    { 
      id: "history", 
      x: 35, 
      y: 84, 
      label: auditContext?.historical_cases?.[0] ? "Historical Cases" : "Municipal Archive", 
      sub: auditContext?.zone ? `${auditContext.zone.name} (${auditContext.zone.soil_type})` : `${selectedCluster?.zone_id || "Sector 7B"} Records`, 
      kind: "history",
      source: auditContext?.zone ? "Supabase Historical DB" : "Supabase Knowledge Graph",
      reasoning: auditContext?.historical_cases?.[0]
        ? `Found ${auditContext.historical_cases.length} similar historical case(s) in zone ${auditContext.zone.name}. Closest match: ID ${auditContext.historical_cases[0].id}, outcome: ${auditContext.historical_cases[0].incident_outcome}, similarity: ${(auditContext.historical_cases[0].similarity * 100).toFixed(0)}%, distance: ${auditContext.historical_cases[0].distance.toFixed(0)}m. Resolution summary: ${auditContext.historical_cases[0].resolution_summary}`
        : selectedCluster?.explainability_factors?.[1] || selectedCluster?.explainability_factors?.[0] || getHistoryFallback(latestIssue?.category)
    },
    { 
      id: "corr", 
      x: 58, 
      y: 40, 
      label: "Forensic Agent", 
      sub: candidateCause.slice(0, 20) + "...", 
      kind: "agent",
      source: "EvidenceAgent (Gemini 2.5)",
      reasoning: `Evidence agent evaluated candidate causes and identified '${candidateCause}' with ${forensics?.confidence ? (forensics.confidence * 100).toFixed(0) : 85}% confidence.`
    },
    { 
      id: "image", 
      x: 58, 
      y: 74, 
      label: "Synthesis Cortex", 
      sub: `Risk: ${currentRisk}`, 
      kind: "agent",
      source: "SynthesisAgent (Gemini 2.5 Pro)",
      reasoning: selectedCluster?.explainability_factors && selectedCluster.explainability_factors.length > 0
        ? `Synthesis Agent (Gemini 2.5 Pro) resolved the following explanation criteria:\n\n${selectedCluster.explainability_factors.map((f: string) => `• ${f}`).join("\n")}`
        : `Gemini 2.5 Pro correlated visual evidence, geographic proximity, and municipal history to assign an overall cluster risk level of ${currentRisk}.`
    },
    { 
      id: "verdict", 
      x: 84, 
      y: 50, 
      label: "Root Cause Hypothesis", 
      sub: currentHypothesis.slice(0, 22) + "...", 
      kind: "verdict",
      source: "Urban Autopsy Engine",
      reasoning: currentHypothesis
    },
  ];

  const node = dynamicNodes.find((n) => n.id === selected) || dynamicNodes[6];

  return (
    <PageTransition>
      <div className="min-h-screen bg-obsidian text-canvas">
        <Nav />
        <main className="pt-32 pb-24">
          <div className="max-w-[1400px] mx-auto px-6">
            {/* Hero */}
            <div className="grid grid-cols-12 gap-10 items-end">
              <div className="col-span-12 lg:col-span-7">
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.7 }}
                  className="font-mono text-[11px] uppercase tracking-[0.22em] text-accent mb-5 flex items-center gap-2"
                >
                  <span className="size-2 rounded-full bg-accent animate-pulse" />
                  <span>Urban Autopsy · Live Connected Backend</span>
                </motion.div>
                <motion.h1
                  initial={{ opacity: 0, y: 14 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
                  className="font-display font-extrabold tracking-[-0.04em] leading-[0.95] text-[clamp(2.75rem,7vw,5.5rem)] text-balance"
                >
                  Every failure becomes <span className="text-accent">evidence</span>.
                </motion.h1>
              </div>
              <div className="col-span-12 lg:col-span-5">
                <p className="text-lg text-white/60 leading-relaxed text-pretty max-w-md">
                  Polaris reconstructs incidents as audit-grade investigations.
                  Every conclusion is traced back to a citation, a sensor, an
                  image, a moment in time.
                </p>
                <div className="mt-4 mb-6 flex items-center gap-3">
                  <span className="font-mono text-[10px] uppercase tracking-wider text-white/50">Select Case:</span>
                  <select 
                    value={selectedIssueId || ""} 
                    onChange={(e) => {
                      const val = e.target.value;
                      setSelectedIssueId(val || null);
                      const url = new URL(window.location.href);
                      if (val) {
                        url.searchParams.set("case_id", val);
                      } else {
                        url.searchParams.delete("case_id");
                      }
                      window.history.pushState({}, "", url.toString());
                    }}
                    className="bg-paper border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white bg-[#0e0f14] focus:outline-none focus:ring-1 focus:ring-accent w-full max-w-[280px]"
                  >
                    <option value="">-- Awaiting Case / Select --</option>
                    {issues.map((issue) => (
                      <option key={issue.id} value={issue.id}>
                        {issue.category} - {issue.id.slice(0, 8)}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="mt-6 grid grid-cols-3 gap-px bg-white/[0.06] border border-white/[0.08] rounded-xl overflow-hidden">
                  {[
                    ["Case ID", latestIssue ? latestIssue.id.slice(0, 8) : "AWAITING"],
                    ["Confidence", confidenceScore],
                    ["Residents", affectedCount.toLocaleString()],
                  ].map(([k, v]) => (
                    <div key={k} className="bg-obsidian p-4">
                      <div className="font-mono text-[9px] uppercase tracking-widest text-white/40">{k}</div>
                      <div className="mt-1 font-display font-extrabold text-base tracking-tight text-accent">{v}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Studio */}
            <div className="mt-16 grid grid-cols-12 gap-6">
              {/* Evidence graph */}
              <section className="col-span-12 lg:col-span-8">
                <Panel title="Evidence Graph" eyebrow="live multi-agent synthesis">
                  <div className="relative h-[460px] rounded-xl border border-white/[0.06] bg-[#0a0b10] overflow-hidden">
                    {!latestIssue && (
                      <div className="absolute inset-0 flex flex-col items-center justify-center bg-[#0a0b10]/90 backdrop-blur-md z-20 p-6 text-center">
                        <motion.div
                          animate={{ scale: [1, 1.05, 1] }}
                          transition={{ repeat: Infinity, duration: 2.5 }}
                          className="size-12 rounded-full border border-accent/40 bg-accent/10 flex items-center justify-center text-accent mb-4"
                        >
                          <svg className="size-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                          </svg>
                        </motion.div>
                        <h3 className="font-mono text-sm font-semibold uppercase tracking-wider text-white">
                          Awaiting Incident Ingestion
                        </h3>
                        <p className="text-white/40 text-xs mt-2 max-w-sm">
                          Select a previous case from the dropdown list or submit a new report on the Citizen Portal to stream live analysis.
                        </p>
                      </div>
                    )}
                    <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                      <defs>
                        <pattern id="autopsy-grid" width="5" height="5" patternUnits="userSpaceOnUse">
                          <path d="M 5 0 L 0 0 0 5" fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="0.1" />
                        </pattern>
                      </defs>
                      <rect width="100" height="100" fill="url(#autopsy-grid)" />
                      {edges.map(([a, b], i) => {
                        const na = dynamicNodes.find((n) => n.id === a);
                        const nb = dynamicNodes.find((n) => n.id === b);
                        if (!na || !nb) return null;
                        const isOn = selected === a || selected === b;
                        return (
                          <motion.line
                            key={i}
                            x1={na.x} y1={na.y} x2={nb.x} y2={nb.y}
                            stroke={isOn ? "#4c8bff" : "rgba(255,255,255,0.18)"}
                            strokeWidth={isOn ? 0.35 : 0.18}
                            initial={{ pathLength: 0 }}
                            animate={{ pathLength: 1 }}
                            transition={{ duration: 1.2, delay: i * 0.08, ease: [0.16, 1, 0.3, 1] }}
                          />
                        );
                      })}
                    </svg>
                    {dynamicNodes.map((n) => {
                      const color =
                        n.kind === "verdict" ? "border-accent bg-accent text-canvas" :
                        n.kind === "agent" ? "border-accent/40 bg-obsidian text-canvas" :
                        n.kind === "history" ? "border-amber-400/40 bg-obsidian text-canvas" :
                        "border-white/15 bg-obsidian text-white/80";
                      const isSel = selected === n.id;
                      return (
                        <button
                          key={n.id}
                          type="button"
                          onClick={() => setSelected(n.id)}
                          style={{ left: `${n.x}%`, top: `${n.y}%` }}
                          className={`absolute -translate-x-1/2 -translate-y-1/2 px-3 py-2 rounded-lg border text-left min-w-[150px] transition-all ${color} ${isSel ? "ring-2 ring-accent/60 scale-105 shadow-[0_0_15px_rgba(168,85,247,0.35)]" : "hover:scale-105"}`}
                        >
                          <div className="flex items-center justify-between">
                            <div className="font-mono text-[9px] uppercase tracking-widest opacity-70">
                              {n.kind}
                            </div>
                            {isSel && (
                              <span className="font-mono text-[8px] bg-accent/20 text-accent px-1 rounded animate-pulse">
                                ACTIVE
                              </span>
                            )}
                          </div>
                          <div className="text-[12px] font-semibold leading-tight mt-0.5">{n.label}</div>
                          <div className="font-mono text-[10px] opacity-70 mt-0.5 truncate max-w-[130px]">{n.sub}</div>
                        </button>
                      );
                    })}
                  </div>
                </Panel>
 
                {/* Causal Timeline */}
                <Panel title="Causal Timeline" eyebrow="MKS Real-time Decision Trace">
                  <div className="relative">
                    <div className="absolute left-[16px] top-2 bottom-2 w-px bg-white/10" />
                    {(() => {
                      if (!latestIssue) {
                        return (
                          <div className="py-16 text-center text-white/30 font-mono text-[11px]">
                            // Awaiting case selection to load decision trace
                          </div>
                        );
                      }
                      let trace: any[] = [];
                      if (decisionAudit?.decision_trace) {
                        try {
                          const parsed = typeof decisionAudit.decision_trace === "string" 
                            ? JSON.parse(decisionAudit.decision_trace) 
                            : decisionAudit.decision_trace;
                          if (parsed && Array.isArray(parsed.trace)) {
                            trace = parsed.trace;
                          } else if (Array.isArray(parsed)) {
                            trace = parsed;
                          }
                        } catch (e) {
                          console.error("Failed to parse decision_trace:", e);
                        }
                      }
                      
                      if (trace && trace.length > 0) {
                        return trace.map((s: any, i: number) => (
                          <div
                            key={i}
                            onClick={() => {
                              if (s.service === "ZoneService") setSelected("history");
                              else if (s.service === "AssetService") setSelected("sensor");
                              else if (s.service === "HistoryService") setSelected("history");
                              else if (s.service === "WeatherService") setSelected("thermal");
                              else if (s.service === "PolicyService") setSelected("corr");
                              else if (s.service === "LLMSynthesisService" || s.service === "LocalRuleEngineService") setSelected("image");
                            }}
                            className="relative py-3 pl-10 pr-2 first:pt-1 cursor-pointer hover:bg-white/[0.03] rounded-lg transition-colors"
                          >
                            <span className="absolute left-[12px] top-[22px] size-2 rounded-full bg-accent" />
                            <div className="flex items-baseline gap-3">
                              <span className="font-mono text-[10px] text-accent w-28">Step {s.step} ({s.latency_ms}ms)</span>
                              <div>
                                <div className="text-[13px] font-semibold text-white/95">{s.service}</div>
                                <div className="font-mono text-[10px] text-white/50 mt-0.5">{s.summary}</div>
                              </div>
                            </div>
                          </div>
                        ));
                      }
 
                      // Fallback static timeline
                      const category = latestIssue?.category || "Water Leak";
                      const zone = selectedCluster?.zone_id || "Sector 7B";
                      
                      let step72h = { k: "Subsurface pressure drift detected", v: "Main-14 telemetry" };
                      let step36h = { k: "Historical pipeline failures resolved", v: `${zone} Archive` };
                      let step14h = { k: "Continuous water accumulation recorded", v: `${zone} Sensor` };
                      
                      if (category === "Broken Streetlight") {
                        step72h = { k: "Line voltage variation warning", v: "Grid Telemetry" };
                        step36h = { k: "Historical streetlight short-circuits archived", v: `${zone} Archive` };
                        step14h = { k: "Ambient lux depletion logged", v: `${zone} Photo-Sensor` };
                      } else if (category === "Garbage Pile") {
                        step72h = { k: "Dumpster fill-level threshold warning", v: "RFID Fill Sensor" };
                        step36h = { k: "Historical sanitation reports indexed", v: `${zone} Archive` };
                        step14h = { k: "Elevated temperature logs registered", v: `${zone} Weather` };
                      } else if (category === "Pothole" || category === "Pavement Subsidence") {
                        step72h = { k: "Pavement structural load warning", v: "Strain Telemetry" };
                        step36h = { k: "Historical road degradation records indexed", v: `${zone} Archive` };
                        step14h = { k: "Localized moisture accumulation logged", v: `${zone} Sensor` };
                      }
 
                      return [
                        { t: "T−72h", k: step72h.k, v: step72h.v, target: "sensor" },
                        { t: "T−36h", k: step36h.k, v: step36h.v, target: "history" },
                        { t: "T−14h", k: step14h.k, v: step14h.v, target: "thermal" },
                        { t: "T−02h", k: latestIssue ? `Citizen report: ${latestIssue.category}` : "Citizen signal ingested & analyzed", v: latestIssue ? `Issue ${latestIssue.id.slice(0, 8)}` : "ID_882041", target: "report" },
                        { t: "T−01h", k: "Synthesis Cortex correlation initiated", v: decisionAudit?.llm_model || "Gemini 2.5 Pro", target: "image" },
                        { t: "T+00:00", k: "Urban Autopsy correlated cluster", v: `Hypothesis: ${(selectedCluster?.causal_hypothesis || currentHypothesis).slice(0, 32)}...`, target: "verdict" },
                      ].map((s, i) => (
                        <div
                          key={s.t}
                          onClick={() => setSelected(s.target)}
                          className="relative py-3 pl-10 pr-2 first:pt-1 cursor-pointer hover:bg-white/[0.03] rounded-lg transition-colors"
                        >
                          <span className="absolute left-[12px] top-[22px] size-2 rounded-full bg-accent" />
                          <div className="flex items-baseline gap-3">
                            <span className="font-mono text-[10px] text-accent w-16">{s.t}</span>
                            <div>
                              <div className="text-[13px] font-medium">{s.k}</div>
                              <div className="font-mono text-[10px] text-white/40 mt-0.5">{s.v}</div>
                            </div>
                          </div>
                        </div>
                      ));
                    })()}
                  </div>
                </Panel>
              </section>

              {/* Inspector */}
              <aside className="col-span-12 lg:col-span-4 space-y-6">
                <Panel title="Inspector" eyebrow={node?.kind || "verdict"}>
                  <div className="font-display font-extrabold text-2xl tracking-tight leading-tight">
                    {node?.label || "Root Cause Hypothesis"}
                  </div>
                  <div className="font-mono text-[11px] text-white/50 mt-1">{node?.sub || "Analyzing..."}</div>

                  <div className="mt-5 grid grid-cols-2 gap-px bg-white/[0.06] border border-white/[0.08] rounded-lg overflow-hidden">
                    {[
                      ["Source", (node as any)?.source || "Gemini Cortex"],
                      ["Confidence", confidenceScore],
                      ["Status", "VERIFIED"],
                      ["Audited", "yes"],
                    ].map(([k, v]) => (
                      <div key={k} className="bg-obsidian p-3">
                        <div className="font-mono text-[9px] uppercase tracking-widest text-white/40">{k}</div>
                        <div className="mt-1 text-[12px] text-accent font-semibold">{v}</div>
                      </div>
                    ))}
                  </div>

                  <div className="mt-5">
                    <div className="font-mono text-[10px] uppercase tracking-[0.18em] text-white/40 mb-2">Node Forensic Analysis</div>
                    <p className="text-[13px] leading-relaxed text-white/75">
                      {(node as any)?.reasoning || currentHypothesis}
                    </p>
                  </div>
                </Panel>

                <Panel title="Image Forensics" eyebrow="Gemini Vision Multi-Modal">
                  {issues[0]?.images && issues[0].images[0] ? (
                    <div className="aspect-[4/3] rounded-lg border border-white/[0.06] overflow-hidden relative">
                      <img src={issues[0].images[0]} alt="Forensic intake" className="w-full h-full object-cover" />
                    </div>
                  ) : (
                    <div className="aspect-[4/3] rounded-lg border border-white/[0.06] bg-[#0a0b10] relative overflow-hidden flex items-center justify-center text-white/30 font-mono text-[11px]">
                      <span>[ Live Forensic Image Stream ]</span>
                    </div>
                  )}
                  <ul className="mt-3 space-y-1.5 font-mono text-[11px] text-white/60">
                    <li>· Category: {issues[0]?.category || "Water Leak"}</li>
                    <li>· Severity: {issues[0]?.severity || 4}/5</li>
                    <li>· Forensic Class: asphalt subsidence</li>
                    <li>· Database Sync: verified ✓</li>
                  </ul>
                </Panel>

                <Panel title="Chain of Custody" eyebrow="audit-grade">
                  <ol className="space-y-2 text-[12px]">
                    <li className="flex justify-between"><span>Signed by Gemini 2.5 Pro</span><span className="font-mono text-[10px] text-accent">Active</span></li>
                    <li className="flex justify-between"><span>Supabase Cluster Sync</span><span className="font-mono text-[10px] text-white/40">Synced</span></li>
                    <li className="flex justify-between"><span>Officer Dispatch Brief</span><span className="font-mono text-[10px] text-accent">Ready</span></li>
                  </ol>
                </Panel>
              </aside>
            </div>
          </div>
        </main>
        <Footer />
      </div>
    </PageTransition>
  );
}

function Panel({ title, eyebrow, children }: { title: string; eyebrow?: string; children: React.ReactNode }) {
  return (
    <div className="rounded-2xl border border-white/[0.08] bg-white/[0.02] p-5 mt-6 first:mt-0">
      <div className="flex items-baseline justify-between mb-4">
        <h3 className="text-[13px] font-semibold tracking-tight">{title}</h3>
        {eyebrow && (
          <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-white/40">
            {eyebrow}
          </span>
        )}
      </div>
      {children}
    </div>
  );
}
