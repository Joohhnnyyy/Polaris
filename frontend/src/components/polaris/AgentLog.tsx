import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { API_URL } from "@/lib/api";

const categoryIcon: Record<string, string> = {
  "Water Leak": "◈",
  "Pothole": "◉",
  "Garbage Pile": "◎",
  "Pavement Subsidence": "⬡",
  "Broken Streetlight": "◐",
};

export function AgentLog() {
  const [issues, setIssues] = useState<any[]>([]);
  const [clusters, setClusters] = useState<any[]>([]);

  useEffect(() => {
    Promise.all([
      fetch(`${API_URL}/issues`).then((r) => r.json()).catch(() => []),
      fetch(`${API_URL}/clusters`).then((r) => r.json()).catch(() => []),
    ]).then(([iss, cls]) => {
      setIssues(iss);
      setClusters(cls);
    });
  }, []);

  // Build live agent log lines from real data
  const latestIssue = issues[0];
  const latestCluster = clusters[0];
  const criticalClusters = clusters.filter((c) => c.risk_level === "CRITICAL");

  const lines = latestIssue && latestCluster ? [
    {
      t: latestIssue.created_at ? new Date(latestIssue.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "—:—:—",
      text: `Citizen report ingested · ${latestIssue.category} · sev ${latestIssue.severity}/5`,
      tone: "muted",
    },
    {
      t: "—",
      text: `Scanning ${latestIssue.lat ? `${Number(latestIssue.lat).toFixed(4)}°N ${Number(latestIssue.lng).toFixed(4)}°E` : "grid coordinates"}…`,
      tone: "muted",
    },
    {
      t: "—",
      text: `Correlation found: ${clusters.length} cluster${clusters.length !== 1 ? "s" : ""} active in zone`,
      tone: "accent",
    },
    {
      t: "—",
      text: `Causal path: ${latestCluster.causal_hypothesis?.slice(0, 60) ?? "Local rule engine analysis"}…`,
      tone: "default",
    },
    {
      t: "—",
      text: `Evidence weight: ${latestCluster.confidence ? (latestCluster.confidence * 100).toFixed(0) : "70"}% · risk=${latestCluster.risk_level}`,
      tone: "muted",
    },
    {
      t: "—",
      text: criticalClusters.length > 0
        ? `${criticalClusters.length} critical cluster${criticalClusters.length > 1 ? "s" : ""} flagged — dispatch package queued`
        : "No critical clusters. Monitoring nominal.",
      tone: criticalClusters.length > 0 ? "success" : "muted",
    },
  ] : [
    { t: "—", text: "Initialising Polaris intelligence layer…", tone: "muted" },
    { t: "—", text: "Connecting to CivicMind API…", tone: "muted" },
    { t: "—", text: "Awaiting live signal…", tone: "accent" },
  ];

  const totalIssues = issues.length;
  const avgConfidence = clusters.length > 0
    ? Math.round(clusters.reduce((s, c) => s + (c.confidence || 0.7), 0) / clusters.length * 100)
    : 0;

  return (
    <section id="intelligence" className="py-32 border-t border-border-subtle bg-canvas">
      <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-12 gap-16 items-start">
        <div className="lg:col-span-5">
          <span className="text-[11px] font-mono text-accent uppercase tracking-[0.22em]">Agent Reasoning</span>
          <h3 className="mt-5 font-display font-extrabold tracking-[-0.03em] text-4xl md:text-[2.75rem] leading-[1.05] text-balance">
            Watch the system think.
          </h3>
          <p className="mt-6 text-slate-muted leading-relaxed max-w-md text-pretty">
            Every Polaris agent narrates its reasoning in real-time. Officers see the chain
            of evidence — not just the verdict — so trust is engineered into the
            interface, not asserted by it.
          </p>

          <div className="mt-10 grid grid-cols-2 gap-px bg-border-subtle border border-border-subtle rounded-lg overflow-hidden">
            {[
              ["Total Incidents", totalIssues > 0 ? totalIssues.toLocaleString() : "…"],
              ["AI Confidence", avgConfidence > 0 ? `${avgConfidence}%` : "…"],
              ["Active Clusters", clusters.length > 0 ? clusters.length.toString() : "…"],
              ["Human Override", "Always"],
            ].map(([k, v]) => (
              <div key={k} className="bg-paper p-5">
                <div className="text-[10px] font-mono text-slate-muted uppercase tracking-widest">{k}</div>
                <div className="mt-1 text-base font-medium">{v}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="lg:col-span-7">
          <div className="rounded-xl border border-border-subtle bg-paper overflow-hidden shadow-[0_20px_60px_-40px_rgba(9,9,11,0.2)]">
            <div className="flex items-center justify-between px-5 py-3 border-b border-border-subtle">
              <div className="flex items-center gap-2">
                <span className="size-1.5 rounded-full bg-accent animate-pulse" />
                <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-slate-muted">
                  polaris.synthesis/live
                </span>
              </div>
              <span className="font-mono text-[10px] text-slate-muted">tail -f</span>
            </div>
            <div className="p-6 font-mono text-[12px] leading-relaxed space-y-2 min-h-[320px]">
              {lines.map((l, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -8 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: i * 0.12 }}
                  className="flex gap-3"
                >
                  <span className="text-slate-muted shrink-0">[{l.t}]</span>
                  <span
                    className={
                      l.tone === "accent"
                        ? "text-accent"
                        : l.tone === "success"
                          ? "text-emerald-600"
                          : l.tone === "muted"
                            ? "text-slate-muted"
                            : "text-obsidian"
                    }
                  >
                    {l.text}
                  </span>
                </motion.div>
              ))}
              <motion.div
                animate={{ opacity: [0.2, 1, 0.2] }}
                transition={{ duration: 1.6, repeat: Infinity }}
                className="text-accent"
              >
                _
              </motion.div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
