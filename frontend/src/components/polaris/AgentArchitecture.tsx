import { motion } from "framer-motion";

const agents = [
  {
    id: "intake",
    name: "Intake Agent",
    model: "Gemini Flash",
    role: "Signal Triage",
    description:
      "First contact for every civic signal. Validates, categorises, embeds, and geo-tags citizen reports before passing them downstream.",
    color: "#3b82f6",
    steps: ["Parse report", "Classify category", "Embed vector", "Geo-tag coords", "Emit to Synthesis"],
    icon: "⬇",
  },
  {
    id: "synthesis",
    name: "Synthesis Agent",
    model: "Gemini 2.5 Pro",
    role: "Urban Autopsy",
    description:
      "Deep multi-hop reasoning engine. Cross-correlates incoming issues with historical telemetry, sensor drift, and causal relations to form a cluster hypothesis.",
    color: "#a855f7",
    steps: ["Query MKS context", "Causal-relation scoring", "LLM hypothesis", "Confidence weighting", "Cluster formation"],
    icon: "⬡",
  },
  {
    id: "evidence",
    name: "Evidence Agent",
    model: "Gemini 2.5 Pro",
    role: "Decision Audit",
    description:
      "Traces every inference back to its primary source. Produces a machine-readable audit trail that is citizen-readable — no black boxes.",
    color: "#10b981",
    steps: ["Trace decision path", "Cite raw sources", "Score evidence chain", "Tag anomaly flags", "Write decision ledger"],
    icon: "◈",
  },
  {
    id: "brief",
    name: "Brief Agent",
    model: "Gemini Flash",
    role: "Dispatch Compiler",
    description:
      "Compiles a structured officer brief from the cluster and evidence record. Routes to the correct team with coordinates, history, and priority.",
    color: "#f59e0b",
    steps: ["Pull cluster record", "Format officer brief", "Attach evidence chain", "Priority routing", "Dispatch + notify"],
    icon: "→",
  },
];

const dataFlow = [
  { from: "Citizen Report", to: "Intake Agent", label: "Raw civic signal" },
  { from: "Intake Agent", to: "Synthesis Agent", label: "Classified + embedded issue" },
  { from: "Synthesis Agent", to: "Evidence Agent", label: "Cluster hypothesis" },
  { from: "Evidence Agent", to: "Brief Agent", label: "Audited decision trace" },
  { from: "Brief Agent", to: "Officer Dashboard", label: "Dispatch brief" },
];

export function AgentArchitecture() {
  return (
    <section
      id="architecture"
      className="py-32 border-t border-border-subtle bg-canvas"
    >
      <div className="max-w-7xl mx-auto px-6">
        {/* Header */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-12 mb-20">
          <div className="md:col-span-5">
            <motion.span
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              className="text-[11px] font-mono text-accent uppercase tracking-[0.22em]"
            >
              Agent Architecture
            </motion.span>
            <motion.h2
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.9, delay: 0.05, ease: [0.16, 1, 0.3, 1] }}
              className="mt-5 font-display font-extrabold tracking-[-0.03em] text-4xl md:text-[2.75rem] leading-[1.05] text-balance"
            >
              Four agents. One neural pipeline.
            </motion.h2>
          </div>
          <div className="md:col-span-7 flex items-end">
            <motion.p
              initial={{ opacity: 0, y: 8 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.9, delay: 0.12 }}
              className="text-slate-muted leading-relaxed text-pretty max-w-xl"
            >
              Each agent has a single purpose, a declared model, and a
              machine-readable audit trail. No shared state, no hidden reasoning.
              The pipeline is inspectable from first signal to final dispatch.
            </motion.p>
          </div>
        </div>

        {/* Data-flow ribbon */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="mb-16 overflow-x-auto pb-2"
        >
          <div className="flex items-center gap-0 min-w-max mx-auto w-fit">
            {dataFlow.map((f, i) => (
              <div key={i} className="flex items-center">
                {/* Node */}
                <div className="flex flex-col items-center">
                  <div
                    className={`px-4 py-2.5 rounded-lg border text-[12px] font-semibold whitespace-nowrap ${
                      f.from === "Citizen Report" || f.from === "Officer Dashboard"
                        ? "border-border-strong bg-paper text-obsidian"
                        : "border-accent/30 bg-accent/[0.06] text-accent"
                    }`}
                  >
                    {f.from}
                  </div>
                </div>
                {/* Arrow + label */}
                <div className="flex flex-col items-center mx-2">
                  <div className="font-mono text-[9px] text-slate-muted uppercase tracking-widest mb-1 whitespace-nowrap">
                    {f.label}
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-12 h-px bg-border-strong" />
                    <span className="text-accent text-[10px]">▶</span>
                  </div>
                </div>
                {/* Last node */}
                {i === dataFlow.length - 1 && (
                  <div className="px-4 py-2.5 rounded-lg border border-border-strong bg-paper text-[12px] font-semibold whitespace-nowrap text-obsidian">
                    {f.to}
                  </div>
                )}
              </div>
            ))}
          </div>
        </motion.div>

        {/* Agent cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5">
          {agents.map((agent, i) => (
            <motion.div
              key={agent.id}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.8, delay: i * 0.09, ease: [0.16, 1, 0.3, 1] }}
              className="group relative rounded-2xl border border-border-subtle bg-paper p-6 hover:border-border-strong transition-colors overflow-hidden"
            >
              {/* Background accent glow */}
              <div
                className="absolute -top-10 -right-10 size-32 rounded-full blur-3xl opacity-0 group-hover:opacity-10 transition-opacity duration-700 pointer-events-none"
                style={{ background: agent.color }}
              />

              {/* Header */}
              <div className="flex items-start justify-between mb-5">
                <div
                  className="size-10 rounded-xl flex items-center justify-center text-[18px] font-bold"
                  style={{ background: `${agent.color}18`, color: agent.color }}
                >
                  {agent.icon}
                </div>
                <div className="text-right">
                  <div
                    className="inline-block px-2 py-0.5 rounded font-mono text-[9px] uppercase tracking-wider font-semibold"
                    style={{ background: `${agent.color}15`, color: agent.color }}
                  >
                    {agent.model}
                  </div>
                </div>
              </div>

              <div className="font-mono text-[9px] uppercase tracking-[0.18em] text-slate-muted mb-1">
                {agent.role}
              </div>
              <h3 className="text-[16px] font-bold tracking-tight mb-3">{agent.name}</h3>
              <p className="text-[12px] text-slate-muted leading-relaxed mb-5 text-pretty">{agent.description}</p>

              {/* Step trace */}
              <div className="space-y-1.5 pt-4 border-t border-border-subtle">
                {agent.steps.map((step, j) => (
                  <motion.div
                    key={j}
                    initial={{ opacity: 0, x: -6 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.09 + j * 0.05, duration: 0.5 }}
                    className="flex items-center gap-2.5"
                  >
                    <span
                      className="size-1.5 rounded-full shrink-0"
                      style={{ background: agent.color, opacity: 0.5 + j * 0.1 }}
                    />
                    <span className="font-mono text-[10px] text-slate-muted">{step}</span>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Bottom note */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.4 }}
          className="mt-12 flex flex-wrap gap-8 justify-center font-mono text-[11px] text-slate-muted"
        >
          {[
            ["4", "Agent classes"],
            ["2", "LLM models (Flash + Pro)"],
            ["100%", "Decision auditability"],
            ["∞", "Signals processed"],
          ].map(([v, k]) => (
            <div key={k} className="flex items-center gap-2">
              <span className="text-accent font-semibold">{v}</span>
              <span>{k}</span>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
