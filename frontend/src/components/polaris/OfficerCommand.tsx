import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import gisMap from "@/assets/gis-map.jpg";
import { API_URL } from "@/lib/api";

const riskColor: Record<string, string> = {
  CRITICAL: "bg-red-500",
  HIGH: "bg-orange-400",
  MEDIUM: "bg-amber-400",
  LOW: "bg-emerald-400",
};

export function OfficerCommand() {
  const [clusters, setClusters] = useState<any[]>([]);
  const [issues, setIssues] = useState<any[]>([]);
  const [briefs, setBriefs] = useState<any[]>([]);

  useEffect(() => {
    Promise.all([
      fetch(`${API_URL}/clusters`).then((r) => r.json()).catch(() => []),
      fetch(`${API_URL}/issues`).then((r) => r.json()).catch(() => []),
      fetch(`${API_URL}/briefs`).then((r) => r.json()).catch(() => []),
    ]).then(([cls, iss, br]) => {
      setClusters(cls);
      setIssues(iss);
      setBriefs(br);
    });
  }, []);

  // Top 3 live alerts from clusters sorted by risk
  const riskOrder = ["CRITICAL", "HIGH", "MEDIUM", "LOW"];
  const topAlerts = [...clusters]
    .sort((a, b) => riskOrder.indexOf(a.risk_level) - riskOrder.indexOf(b.risk_level))
    .slice(0, 3)
    .map((c, idx) => ({
      id: `CLUSTER #${c.id.slice(0, 6).toUpperCase()}`,
      title: c.causal_hypothesis?.split(":").pop()?.trim().slice(0, 40) ?? "Active infrastructure anomaly",
      sub: `${c.zone_id || "Sector 7B"} · Risk ${c.risk_level}`,
      risk: c.risk_level,
    }));

  const totalIssues = issues.length;
  const pendingBriefs = briefs.filter((b) => b.status !== "APPROVED").length;
  const avgConfidence = clusters.length > 0
    ? Math.round(clusters.reduce((s, c) => s + (c.confidence || 0.7), 0) / clusters.length * 100)
    : 0;

  return (
    <section id="officers" className="relative py-32 bg-obsidian text-canvas overflow-hidden">
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/15 to-transparent" />

      <div className="max-w-7xl mx-auto px-6 relative">
        <div className="max-w-2xl mb-20">
          <span className="text-[11px] font-mono uppercase tracking-[0.22em] text-accent">Officer Command</span>
          <h2 className="mt-5 font-display font-extrabold tracking-[-0.03em] text-4xl md:text-5xl leading-[1.05] text-balance">
            A precision interface for those who run the city.
          </h2>
          <p className="mt-6 text-white/60 leading-relaxed max-w-lg text-pretty">
            No clutter. No decoration. Every pixel earns its place. Built with
            officers, dispatchers, and engineers in the room — not after.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-5">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
            className="lg:col-span-3 relative h-[560px] rounded-xl border border-white/10 overflow-hidden"
          >
            <img
              src={gisMap}
              alt="GIS intelligence interface"
              loading="lazy"
              width={1600}
              height={1008}
              className="absolute inset-0 size-full object-cover opacity-90"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-obsidian/60 via-transparent to-transparent" />

            {/* Live Alerts Panel */}
            <div className="absolute top-5 left-5 w-[300px] p-5 rounded-lg border border-white/10 bg-obsidian/80 backdrop-blur">
              <div className="flex items-center justify-between mb-5">
                <span className="text-[10px] font-mono uppercase tracking-[0.18em] text-accent">Live Alerts</span>
                <span className="size-1.5 rounded-full bg-red-500 animate-pulse" />
              </div>
              <div className="space-y-3">
                {topAlerts.length > 0 ? topAlerts.map((a) => (
                  <div
                    key={a.id}
                    className="p-3 rounded border border-white/5 bg-white/[0.04] hover:bg-white/[0.07] transition-colors"
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`size-1.5 rounded-full shrink-0 ${riskColor[a.risk] || "bg-white/40"}`} />
                      <span className="font-mono text-[10px] text-white/40">{a.id}</span>
                    </div>
                    <div className="text-[13px] font-medium">{a.title}</div>
                    <div className="font-mono text-[10px] mt-1.5 text-white/40">{a.sub}</div>
                  </div>
                )) : (
                  <div className="p-3 rounded border border-white/5 bg-white/[0.04] text-[12px] text-white/40 font-mono">
                    Awaiting cluster data…
                  </div>
                )}
              </div>
            </div>

            <div className="absolute bottom-5 right-5 flex items-center gap-2 px-3 py-1.5 rounded-md border border-white/10 bg-obsidian/70 backdrop-blur">
              <span className="size-1.5 rounded-full bg-accent animate-pulse" />
              <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-white/70">
                GIS · {issues.length} events live
              </span>
            </div>
          </motion.div>

          <div className="space-y-5">
            <Card>
              <Label>Incidents Live</Label>
              <Value>{totalIssues > 0 ? totalIssues.toLocaleString() : "…"}</Value>
              <div className="mt-4 h-1 w-full bg-white/10 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  whileInView={{ width: `${Math.min(100, (totalIssues / 200) * 100)}%` }}
                  viewport={{ once: true }}
                  transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
                  className="h-full bg-accent"
                />
              </div>
            </Card>
            <Card>
              <Label>AI Confidence</Label>
              <Value>{avgConfidence > 0 ? `${avgConfidence}%` : "…"}</Value>
              <div className="mt-4 grid grid-cols-12 gap-px">
                {Array.from({ length: 12 }).map((_, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.04, duration: 0.4 }}
                    className="h-4 bg-accent"
                    style={{ opacity: 0.2 + (i / 12) * 0.8 }}
                  />
                ))}
              </div>
            </Card>
            <Card accent>
              <div className="text-[13px] font-semibold mb-2">
                {pendingBriefs > 0 ? `${pendingBriefs} Brief${pendingBriefs > 1 ? "s" : ""} Pending` : "Dispatch Ready"}
              </div>
              <p className="text-[12px] text-white/60 leading-relaxed">
                {clusters.length} active cluster{clusters.length !== 1 ? "s" : ""} tracked across {
                  [...new Set(clusters.map((c) => c.zone_id).filter(Boolean))].length || 1
                } zone{[...new Set(clusters.map((c) => c.zone_id).filter(Boolean))].length !== 1 ? "s" : ""}.{" "}
                {pendingBriefs > 0 ? "Officer review required." : "All dispatches resolved."}
              </p>
            </Card>
          </div>
        </div>
      </div>

      <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-accent/40 to-transparent" />
    </section>
  );
}

function Card({ children, accent }: { children: React.ReactNode; accent?: boolean }) {
  return (
    <div className={`p-5 rounded-xl border ${accent ? "border-accent/30 bg-accent/10" : "border-white/10 bg-white/[0.04]"}`}>
      {children}
    </div>
  );
}

function Label({ children }: { children: React.ReactNode }) {
  return <div className="text-[10px] font-mono uppercase tracking-[0.18em] text-white/50 mb-2">{children}</div>;
}

function Value({ children }: { children: React.ReactNode }) {
  return <div className="font-display text-3xl font-extrabold tracking-tight tabular-nums">{children}</div>;
}
