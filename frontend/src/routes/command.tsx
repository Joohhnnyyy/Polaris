import { createFileRoute } from "@tanstack/react-router";
import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";
import { Nav } from "@/components/polaris/Nav";
import { PageTransition } from "@/components/polaris/PageTransition";
import { API_URL, WS_URL } from "@/lib/api";

export const Route = createFileRoute("/command")({
  head: () => ({
    meta: [
      { title: "Officer Command Center — Polaris" },
      {
        name: "description",
        content:
          "Enterprise command surface for civic operators. Risk clusters, AI intelligence briefs, work order approvals, infrastructure health, all in one operational picture.",
      },
      { property: "og:title", content: "Polaris Command Center" },
      {
        property: "og:description",
        content: "Run the city from a single operational console.",
      },
    ],
  }),
  component: CommandPage,
});

function CommandPage() {
  return (
    <PageTransition>
      <div className="min-h-screen bg-obsidian text-canvas">
        <Nav />
        <main className="pt-20">
          <CommandShell />
        </main>
      </div>
    </PageTransition>
  );
}

const darkMapStyles = [
  { elementType: "geometry", stylers: [{ color: "#0c0d12" }] },
  { elementType: "labels.text.stroke", stylers: [{ color: "#0c0d12" }] },
  { elementType: "labels.text.fill", stylers: [{ color: "#7f8497" }] },
  { featureType: "administrative.locality", elementType: "labels.text.fill", stylers: [{ color: "#a855f7" }] },
  { featureType: "poi", stylers: [{ visibility: "off" }] },
  { featureType: "road", elementType: "geometry", stylers: [{ color: "#181a23" }] },
  { featureType: "road", elementType: "geometry.stroke", stylers: [{ color: "#252836" }] },
  { featureType: "road", elementType: "labels.text.fill", stylers: [{ color: "#6b7280" }] },
  { featureType: "road.highway", elementType: "geometry", stylers: [{ color: "#252836" }] },
  { featureType: "road.highway", elementType: "geometry.stroke", stylers: [{ color: "#374151" }] },
  { featureType: "water", elementType: "geometry", stylers: [{ color: "#080c16" }] },
  { featureType: "water", elementType: "labels.text.fill", stylers: [{ color: "#3b82f6" }] },
];

const categoryColorMap: Record<string, string> = {
  "Water Leak": "#3b82f6",
  "Pothole": "#f43f5e",
  "Garbage Pile": "#10b981",
  "Pavement Subsidence": "#a855f7",
  "Broken Streetlight": "#eab308",
};

function CommandMapCanvas({ issues }: { issues: any[] }) {
  const [apiKey, setApiKey] = useState("");
  const [mapLoaded, setMapLoaded] = useState(false);

  useEffect(() => {
    fetch(`${API_URL}/config`)
      .then((r) => r.json())
      .then((d) => { if (d.google_maps_key) setApiKey(d.google_maps_key); })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!apiKey) return;
    if ((window as any).google?.maps) { setMapLoaded(true); return; }
    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=geometry`;
    script.async = true;
    script.defer = true;
    script.onload = () => setMapLoaded(true);
    document.head.appendChild(script);
  }, [apiKey]);

  useEffect(() => {
    if (!mapLoaded) return;
    const mapEl = document.getElementById("command-map-canvas");
    if (!mapEl) return;

    const map = new (window as any).google.maps.Map(mapEl, {
      center: { lat: 28.582, lng: 77.262 },
      zoom: 13,
      styles: darkMapStyles,
      disableDefaultUI: true,
      zoomControl: true,
      zoomControlOptions: {
        position: (window as any).google.maps.ControlPosition.RIGHT_CENTER,
      },
    });

    issues.forEach((issue) => {
      if (!issue.lat || !issue.lng) return;
      const color = categoryColorMap[issue.category] || "#9ca3af";
      const marker = new (window as any).google.maps.Marker({
        position: { lat: Number(issue.lat), lng: Number(issue.lng) },
        map,
        title: issue.category,
        icon: {
          path: (window as any).google.maps.SymbolPath.CIRCLE,
          scale: 7,
          fillColor: color,
          fillOpacity: 0.9,
          strokeColor: "#ffffff",
          strokeWeight: 1.5,
        },
      });
      const infoWindow = new (window as any).google.maps.InfoWindow({
        content: `
          <div style="color:#0f172a;font-family:sans-serif;padding:6px;min-width:180px;">
            <div style="font-size:11px;font-weight:800;text-transform:uppercase;color:${color};letter-spacing:0.05em;">${issue.category}</div>
            <div style="font-size:13px;font-weight:bold;margin-top:2px;">Severity ${issue.severity}/5</div>
            <div style="font-size:11px;color:#64748b;margin-top:1px;">Coords: (${Number(issue.lat).toFixed(4)}, ${Number(issue.lng).toFixed(4)})</div>
            <p style="font-size:12px;margin:6px 0 0 0;color:#334155;line-height:1.4;">${(issue.description || "").slice(0, 120)}</p>
          </div>
        `,
      });
      marker.addListener("click", () => infoWindow.open(map, marker));
    });
  }, [mapLoaded, issues]);

  return (
    <div className="absolute inset-0">
      {!mapLoaded && (
        <div className="absolute inset-0 flex items-center justify-center text-white/20 font-mono text-[11px] tracking-widest">
          LOADING MAP…
        </div>
      )}
      <div id="command-map-canvas" className="w-full h-full" />
    </div>
  );
}

function CommandShell() {
  const [clusters, setClusters] = useState<any[]>([]);
  const [issues, setIssues] = useState<any[]>([]);
  const [briefs, setBriefs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  async function fetchAllData() {
    try {
      const [clustersRes, issuesRes, briefsRes] = await Promise.all([
        fetch(`${API_URL}/clusters`),
        fetch(`${API_URL}/issues`),
        fetch(`${API_URL}/briefs`)
      ]);
      if (clustersRes.ok) setClusters(await clustersRes.json());
      if (issuesRes.ok) setIssues(await issuesRes.json());
      if (briefsRes.ok) setBriefs(await briefsRes.json());
    } catch (err) {
      console.error("Failed to fetch command center data:", err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchAllData();

    // WebSocket Auto-Refresh Sync
    const ws = new WebSocket(`${WS_URL}/ws/logs`);
    ws.onmessage = () => {
      fetchAllData();
    };

    return () => {
      ws.close();
    };
  }, []);

  const handleApprove = async (briefId: string) => {
    try {
      const res = await fetch(`${API_URL}/briefs/${briefId}/approve`, {
        method: "POST"
      });
      if (res.ok) {
        fetchAllData();
      }
    } catch (err) {
      console.error("Approval request failed:", err);
    }
  };

  const activeCount = issues.filter(i => i.status !== "RESOLVED").length;
  const pendingBriefs = briefs.filter(b => b.status === "PENDING_REVIEW" || b.status === "SENT");

  return (
    <div className="px-4 md:px-6 pb-10">
      {/* Top operational bar */}
      <div className="border border-white/[0.08] rounded-2xl bg-white/[0.02] overflow-hidden">
        <div className="grid grid-cols-2 md:grid-cols-6 divide-y md:divide-y-0 md:divide-x divide-white/[0.06]">
          <StatPill label="Active Incidents" value={activeCount ? activeCount.toString() : "0"} delta="+Live" positive />
          <StatPill label="Open Work Orders" value={pendingBriefs.length.toString()} delta="-review" positive />
          <StatPill label="At-Risk Assets" value={clusters.length ? (clusters.length * 3).toString() : "0"} delta="watching" muted />
          <StatPill label="Crews in Field" value="22 / 28" />
          <StatPill label="SLA Compliance" value="99.4%" positive />
          <StatPill label="Synced Latency" value="06ms" muted />
        </div>
      </div>

      {/* Main grid */}
      <div className="mt-6 grid grid-cols-12 gap-6">
        {/* Left rail: risk clusters */}
        <section className="col-span-12 lg:col-span-3 space-y-6">
          <Panel title="Risk Clusters" eyebrow="ranked by composite score">
            <ul className="divide-y divide-white/[0.06]">
              {clusters.length > 0 ? (
                clusters.map((c) => {
                  const score = c.risk_level === "CRITICAL" ? 0.98 : (c.risk_level === "HIGH" ? 0.88 : (c.risk_level === "MEDIUM" ? 0.65 : 0.35));
                  return (
                    <li key={c.id} className="py-3.5 first:pt-0 last:pb-0">
                      <div className="flex items-baseline justify-between gap-2">
                        <span className="text-[13px] font-medium truncate max-w-[200px]" title={c.causal_hypothesis}>
                          {c.causal_hypothesis ? c.causal_hypothesis.replace("[Local Rule Engine] Causal failure path: ", "") : "Failure Risk Path"}
                        </span>
                        <span className="font-mono text-[11px] text-accent tabular-nums">
                          {score.toFixed(2)}
                        </span>
                      </div>
                      <div className="mt-1.5 flex items-center gap-2">
                        <div className="flex-1 h-1 bg-white/[0.06] rounded-full overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${score * 100}%` }}
                            transition={{ duration: 1.1, ease: [0.16, 1, 0.3, 1] }}
                            className="h-full bg-accent"
                          />
                        </div>
                        <span className="font-mono text-[10px] text-white/40">{c.zone_id || "Sector 7B"}</span>
                      </div>
                    </li>
                  );
                })
              ) : (
                <div className="py-6 text-center text-white/30 font-mono text-[11px]">
                  [ No active risk clusters ]
                </div>
              )}
            </ul>
          </Panel>

          <Panel title="Infrastructure Health" eyebrow="last 24h">
            {[
              ["Water", 0.99, "nominal"],
              ["Power", 0.97, "nominal"],
              ["Transit", 0.91, "watch"],
              ["Sanitation", 0.95, "nominal"],
              ["Lighting", 0.88, "degraded"],
            ].map(([k, v, status]) => (
              <div key={k as string} className="py-2.5 first:pt-0 last:pb-0">
                <div className="flex justify-between text-[12px]">
                  <span>{k as string}</span>
                  <span className={`font-mono text-[10px] uppercase tracking-wider ${
                    status === "nominal" ? "text-emerald-400" : status === "watch" ? "text-amber-400" : "text-rose-400"
                  }`}>
                    {status as string}
                  </span>
                </div>
                <div className="mt-1.5 h-1 bg-white/[0.06] rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(v as number) * 100}%` }}
                    transition={{ duration: 1.1, ease: [0.16, 1, 0.3, 1] }}
                    className={`h-full ${status === "degraded" ? "bg-rose-400" : status === "watch" ? "bg-amber-400" : "bg-emerald-400"}`}
                  />
                </div>
              </div>
            ))}
          </Panel>
        </section>

        {/* Center: map + brief */}
        <section className="col-span-12 lg:col-span-6 space-y-6">
          <Panel title="Operational Picture" eyebrow="GIS · real-time">
            <div className="relative h-[440px] rounded-lg overflow-hidden border border-white/[0.06] bg-[#0b0c10]">
              <CommandMapCanvas issues={issues} />
              <div className="absolute top-3 left-3 px-2.5 py-1 rounded-md bg-obsidian/70 backdrop-blur border border-white/10 font-mono text-[10px] uppercase tracking-[0.18em]">
                Live · {issues.length} events
              </div>
              <div className="absolute bottom-3 right-3 flex gap-2">
                {Object.entries(categoryColorMap).map(([label, color]) => (
                  <span key={label} className="flex items-center gap-1 px-2 py-1 rounded bg-obsidian/70 backdrop-blur border border-white/10 font-mono text-[10px]">
                    <span className="size-1.5 rounded-full inline-block" style={{ background: color }} />
                    {label.split(" ")[0]}
                  </span>
                ))}
              </div>
            </div>
          </Panel>

          <Panel title="AI Intelligence Brief" eyebrow="generated live">
            <div className="space-y-3 text-[13px] leading-relaxed text-white/75">
              {clusters.length > 0 ? (
                clusters.slice(0, 3).map((c, idx) => (
                  <p key={c.id}>
                    <span className="text-accent font-mono text-[11px] mr-2">0{idx + 1}</span>
                    {c.causal_hypothesis ? c.causal_hypothesis : "Cross-correlated telemetry reports active sector failure path."} Ingested in zone {c.zone_id || "Sector 7B"} with {c.confidence ? Math.round(c.confidence * 100) : 70}% model confidence. Recommended immediate site inspection.
                  </p>
                ))
              ) : (
                <p>
                  <span className="text-accent font-mono text-[11px] mr-2">01</span>
                  No critical anomalies resolved. Citywide systems nominal.
                </p>
              )}
            </div>
          </Panel>
        </section>

        {/* Right rail: work orders */}
        <section className="col-span-12 lg:col-span-3 space-y-6">
          <Panel title="Work Order Queue" eyebrow="awaiting approval">
            <ul className="space-y-3">
              {briefs.length > 0 ? (
                briefs.map((b) => (
                  <li key={b.id} className="p-3 rounded-lg border border-white/[0.08] bg-white/[0.02]">
                    <div className="flex justify-between items-baseline">
                      <span className="font-mono text-[10px] text-white/40">WO-{b.id.slice(0, 4).toUpperCase()}</span>
                      <span className={`font-mono text-[10px] uppercase ${b.status === "APPROVED" ? "text-emerald-400" : "text-accent"}`}>
                        {b.status}
                      </span>
                    </div>
                    <div className="mt-1 text-[13px] font-medium">
                      {b.clusters?.causal_hypothesis ? b.clusters.causal_hypothesis.replace("[Local Rule Engine] Causal failure path: ", "") : `${b.zone_id} Dispatch Brief`}
                    </div>
                    <div className="mt-1 font-mono text-[10px] text-white/40">Field Crew 04</div>
                    <div className="mt-3 flex gap-2">
                      {b.status !== "APPROVED" ? (
                        <>
                          <button
                            onClick={() => handleApprove(b.id)}
                            className="flex-1 px-2.5 py-1.5 rounded bg-accent text-canvas text-[11px] font-medium hover:opacity-90 transition"
                          >
                            Approve
                          </button>
                          <button className="px-2.5 py-1.5 rounded border border-white/10 text-[11px] text-white/70 hover:bg-white/[0.04] transition">
                            Defer
                          </button>
                        </>
                      ) : (
                        <div className="text-[11px] text-emerald-400/80 font-semibold py-1">
                          ✓ Work Order Approved & Dispatched
                        </div>
                      )}
                    </div>
                  </li>
                ))
              ) : (
                <div className="py-6 text-center text-white/30 font-mono text-[11px]">
                  [ No pending work orders ]
                </div>
              )}
            </ul>
          </Panel>

          <Panel title="Crew Telemetry" eyebrow="live">
            <ul className="space-y-2.5 text-[12px]">
              {[
                ["Crew 04", "en route · 6 min"],
                ["Crew 07", "on-site · 22 min"],
                ["Crew 12", "standby"],
                ["Crew 19", "returning"],
              ].map(([c, s]) => (
                <li key={c} className="flex justify-between">
                  <span>{c}</span>
                  <span className="font-mono text-[11px] text-white/50">{s}</span>
                </li>
              ))}
            </ul>
          </Panel>
        </section>
      </div>
    </div>
  );
}


function StatPill({ label, value, delta, positive, muted }: { label: string; value: string; delta?: string; positive?: boolean; muted?: boolean }) {
  return (
    <div className="p-4 md:p-5">
      <div className="font-mono text-[10px] uppercase tracking-[0.18em] text-white/40">
        {label}
      </div>
      <div className="mt-1.5 flex items-baseline gap-2">
        <span className="font-display font-extrabold tracking-tight text-2xl tabular-nums">
          {value}
        </span>
        {delta && (
          <span className={`font-mono text-[10px] ${muted ? "text-white/40" : positive ? "text-emerald-400" : "text-rose-400"}`}>
            {delta}
          </span>
        )}
      </div>
    </div>
  );
}

function Panel({ title, eyebrow, children }: { title: string; eyebrow?: string; children: React.ReactNode }) {
  return (
    <div className="rounded-2xl border border-white/[0.08] bg-white/[0.02] p-5">
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
