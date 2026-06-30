import { motion } from "framer-motion";

/* ──────────────────────────────────────────────────────────────
   Stage 01 — Omniscient Ingestion
   Dark panel · 6 live streaming sensor channels converging
────────────────────────────────────────────────────────────── */
function IngestionDiagram() {
  const channels = [
    { label: "SCADA · Water", color: "#3b82f6", delay: 0 },
    { label: "IoT Meters", color: "#8b5cf6", delay: 0.28 },
    { label: "Traffic Sensors", color: "#10b981", delay: 0.56 },
    { label: "Citizen Reports", color: "#f59e0b", delay: 0.84 },
    { label: "Power Grid", color: "#ef4444", delay: 1.12 },
    { label: "Weather / Env", color: "#06b6d4", delay: 1.4 },
  ];

  return (
    <div className="w-full h-full bg-[#f7f8fc] flex flex-col justify-center px-8 py-6 gap-3 relative overflow-hidden">
      {/* Grid pattern */}
      <div className="absolute inset-0 opacity-[0.06]"
        style={{ backgroundImage: "linear-gradient(#94a3b8 1px, transparent 1px), linear-gradient(90deg, #94a3b8 1px, transparent 1px)", backgroundSize: "32px 32px" }} />

      {/* Glow blob */}
      <div className="absolute -top-10 right-0 w-72 h-48 rounded-full bg-blue-400/10 blur-3xl pointer-events-none" />
      <div className="absolute -bottom-10 left-0 w-48 h-48 rounded-full bg-purple-400/10 blur-3xl pointer-events-none" />

      {/* Label */}
      <div className="absolute top-4 left-5 font-mono text-[9px] uppercase tracking-[0.22em] text-slate-400">Stage 01 · Signal Ingestion</div>
      <div className="absolute top-4 right-5 flex items-center gap-1.5">
        <span className="size-1.5 rounded-full bg-emerald-500 animate-pulse" />
        <span className="font-mono text-[9px] text-emerald-600 uppercase tracking-widest">Live</span>
      </div>

      {/* Channels */}
      <div className="flex flex-col gap-2.5 mt-6">
        {channels.map((ch, i) => (
          <div key={ch.label} className="flex items-center gap-3">
            {/* Source label */}
            <div className="w-28 shrink-0 text-right">
              <span className="font-mono text-[9px] tracking-wide" style={{ color: `${ch.color}99` }}>
                {ch.label}
              </span>
            </div>
            {/* Track */}
            <div className="flex-1 h-6 rounded-md relative overflow-hidden"
              style={{ background: `${ch.color}10`, border: `1px solid ${ch.color}30` }}>
              {/* Moving pulses */}
              {[0, 1, 2, 3, 4].map((p) => (
                <motion.div
                  key={p}
                  className="absolute inset-y-0"
                  style={{ left: "-10px", width: "calc(100% + 20px)" }}
                  initial={{ x: "-100%", opacity: 0 }}
                  animate={{ x: "0%", opacity: [0, 1, 1, 0] }}
                  transition={{
                    duration: 2.2,
                    delay: ch.delay + p * 0.44,
                    repeat: Infinity,
                    ease: "linear",
                  }}
                >
                  <div
                    className="absolute top-1/2 -translate-y-1/2 right-0 rounded-full"
                    style={{ width: 6, height: 6, background: ch.color, boxShadow: `0 0 8px ${ch.color}` }}
                  />
                </motion.div>
              ))}
              {/* Baseline */}
              <div className="absolute inset-x-0 top-1/2 -translate-y-px h-px"
                style={{ background: `linear-gradient(90deg, transparent, ${ch.color}50, transparent)` }} />
            </div>
            {/* Endpoint dot */}
            <div className="size-2 rounded-full shrink-0" style={{ background: ch.color, boxShadow: `0 0 5px ${ch.color}60` }} />
          </div>
        ))}
      </div>

      {/* Convergence bar */}
      <div className="flex items-center gap-3 mt-3 pt-3 border-t border-slate-200">
        <div className="w-28 shrink-0" />
        <motion.div
          className="flex-1 h-7 rounded-md flex items-center justify-center gap-2"
          style={{ background: "linear-gradient(90deg, #3b82f608, #8b5cf608, #10b98108)", border: "1px solid #3b82f630" }}
          animate={{ opacity: [0.8, 1, 0.8] }}
          transition={{ duration: 2.4, repeat: Infinity }}
        >
          <span className="size-1.5 rounded-full bg-accent animate-pulse" />
          <span className="font-mono text-[9px] text-slate-500 uppercase tracking-[0.2em]">Unified Civic Substrate</span>
        </motion.div>
        <div className="size-2 shrink-0" />
      </div>
    </div>
  );
}

/* ──────────────────────────────────────────────────────────────
   Stage 02 — Correlation Engine
   Dark · Issue nodes → Synthesis Agent → Cluster
────────────────────────────────────────────────────────────── */
function CorrelationDiagram() {
  const issues = [
    { label: "Water Leak", color: "#3b82f6", cy: 60 },
    { label: "Pavement", color: "#a855f7", cy: 120 },
    { label: "Pressure", color: "#06b6d4", cy: 180 },
    { label: "Citizen", color: "#f59e0b", cy: 240 },
  ];

  return (
    <div className="w-full h-full bg-[#f7f8fc] relative overflow-hidden">
      {/* Grid */}
      <div className="absolute inset-0 opacity-[0.06]"
        style={{ backgroundImage: "linear-gradient(#94a3b8 1px, transparent 1px), linear-gradient(90deg, #94a3b8 1px, transparent 1px)", backgroundSize: "32px 32px" }} />

      {/* Glows */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 size-64 rounded-full bg-purple-300/15 blur-3xl pointer-events-none" />
      <div className="absolute top-4 left-5 font-mono text-[9px] uppercase tracking-[0.22em] text-slate-400">Stage 02 · Correlation Engine</div>

      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 640 320" preserveAspectRatio="xMidYMid meet">
        <defs>
          {issues.map((iss) => (
            <filter key={iss.label} id={`glow-${iss.label.replace(" ","")}`}>
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
            </filter>
          ))}
          <filter id="glow-agent">
            <feGaussianBlur stdDeviation="6" result="blur" />
            <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
          <filter id="glow-cluster">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        </defs>

        {/* Connecting beams from issues to agent */}
        {issues.map((iss, i) => (
          <g key={iss.label}>
            <motion.line
              x1={110} y1={iss.cy}
              x2={295} y2={160}
              stroke={iss.color} strokeWidth={1.2} strokeOpacity={0.4}
              initial={{ pathLength: 0, opacity: 0 }}
              whileInView={{ pathLength: 1, opacity: 0.4 }}
              viewport={{ once: true }}
              transition={{ delay: 0.5 + i * 0.1, duration: 0.6 }}
            />
            {/* Travelling data packet */}
            <motion.circle r={3} fill={iss.color}
              style={{ filter: `drop-shadow(0 0 4px ${iss.color})` }}
              initial={{ cx: 110, cy: iss.cy, opacity: 0 }}
              animate={{ cx: [110, 295], cy: [iss.cy, 160], opacity: [0, 1, 0] }}
              transition={{ delay: 0.8 + i * 0.3, duration: 1.2, repeat: Infinity, repeatDelay: 1.5, ease: "easeInOut" }}
            />
          </g>
        ))}

        {/* Issue nodes */}
        {issues.map((iss, i) => (
          <g key={iss.label}>
            <motion.circle cx={80} cy={iss.cy} r={26}
              fill={`${iss.color}15`} stroke={iss.color} strokeWidth={1.5} strokeOpacity={0.8}
              style={{ filter: `drop-shadow(0 0 8px ${iss.color}50)` }}
              initial={{ scale: 0, opacity: 0 }}
              whileInView={{ scale: 1, opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.12, duration: 0.5, type: "spring" }}
            />
            <text x={80} y={iss.cy + 4} textAnchor="middle" fontSize={8} fill={iss.color}
              fontFamily="monospace" fontWeight="700" opacity={1}>
              {iss.label.split(" ")[0]}
            </text>
          </g>
        ))}

        {/* Synthesis Agent — centre */}
        {/* Outer pulse ring */}
        <motion.circle cx={320} cy={160} r={58} fill="none" stroke="#a855f7" strokeWidth={0.5} strokeOpacity={0.3}
          animate={{ r: [58, 68, 58], opacity: [0.3, 0.1, 0.3] }}
          transition={{ duration: 2.8, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.circle cx={320} cy={160} r={46} fill="#a855f715" stroke="#a855f7" strokeWidth={1.5}
          style={{ filter: "drop-shadow(0 0 12px #a855f760)" }}
          initial={{ scale: 0 }} whileInView={{ scale: 1 }} viewport={{ once: true }}
          transition={{ delay: 0.55, duration: 0.7, type: "spring" }}
        />
        <text x={320} y={155} textAnchor="middle" fontSize={8} fill="#7c3aed"
          fontFamily="monospace" fontWeight="800" letterSpacing="1">SYNTHESIS</text>
        <text x={320} y={169} textAnchor="middle" fontSize={7} fill="#7c3aed"
          fontFamily="monospace" opacity={0.8}>AGENT</text>

        {/* Arrow to cluster */}
        <motion.line x1={368} y1={160} x2={440} y2={160}
          stroke="#dc2626" strokeWidth={1.5} strokeOpacity={0.7}
          strokeDasharray="4 3"
          initial={{ pathLength: 0 }} whileInView={{ pathLength: 1 }} viewport={{ once: true }}
          transition={{ delay: 1.1, duration: 0.5 }}
        />
        <text x={404} y={152} textAnchor="middle" fontSize={7} fill="#dc2626" fontFamily="monospace" opacity={0.7}>→ cluster</text>

        {/* Cluster output */}
        <motion.rect x={444} y={118} width={150} height={84} rx={10}
          fill="#ef444412" stroke="#ef4444" strokeWidth={1.5} strokeOpacity={0.7}
          style={{ filter: "drop-shadow(0 0 10px #ef444440)" }}
          initial={{ opacity: 0, x: 16 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}
          transition={{ delay: 1.2, duration: 0.6 }}
        />
        <text x={519} y={143} textAnchor="middle" fontSize={8} fill="#dc2626"
          fontFamily="monospace" fontWeight="800">CLUSTER</text>
        <text x={519} y={157} textAnchor="middle" fontSize={7} fill="#dc2626"
          fontFamily="monospace" opacity={0.9}>CRITICAL · 87%</text>
        <text x={519} y={170} textAnchor="middle" fontSize={7} fill="#dc2626"
          fontFamily="monospace" opacity={0.7}>Sector 7B</text>
        <rect x={468} y={181} width={102} height={12} rx={3} fill="#ef444415" />
        <text x={519} y={190} textAnchor="middle" fontSize={6.5} fill="#dc2626"
          fontFamily="monospace">Subgrade wash-out</text>

        {/* Bottom caption */}
        <text x={320} y={308} textAnchor="middle" fontSize={7.5} fill="#94a3b8"
          fontFamily="monospace">Causal scoring · MKS context · LLM hypothesis generation</text>
      </svg>
    </div>
  );
}

/* ──────────────────────────────────────────────────────────────
   Stage 03 — Predictive Dispatch
   Dark · Cluster → Evidence → Brief card → Officer
────────────────────────────────────────────────────────────── */
function DispatchDiagram() {
  const nodes = [
    { cx: 80,  label: "Cluster",  sub: "CRITICAL", color: "#ef4444" },
    { cx: 213, label: "Evidence", sub: "87% conf", color: "#10b981" },
    { cx: 346, label: "Brief",    sub: "compiled",  color: "#f59e0b" },
    { cx: 479, label: "Officer",  sub: "dispatched", color: "#3b82f6" },
  ];

  return (
    <div className="w-full h-full bg-[#f7f8fc] relative overflow-hidden">
      <div className="absolute inset-0 opacity-[0.06]"
        style={{ backgroundImage: "linear-gradient(#94a3b8 1px, transparent 1px), linear-gradient(90deg, #94a3b8 1px, transparent 1px)", backgroundSize: "32px 32px" }} />

      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-32 rounded-full bg-blue-400/8 blur-3xl pointer-events-none" />
      <div className="absolute top-4 left-5 font-mono text-[9px] uppercase tracking-[0.22em] text-slate-400">Stage 03 · Predictive Dispatch</div>

      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 590 310" preserveAspectRatio="xMidYMid meet">
        <defs>
          <linearGradient id="pipe-grad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#ef4444" stopOpacity="0.4" />
            <stop offset="33%" stopColor="#10b981" stopOpacity="0.4" />
            <stop offset="66%" stopColor="#f59e0b" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.4" />
          </linearGradient>
        </defs>

        {/* Background pipe */}
        <motion.rect x={42} y={154} width={510} height={4} rx={2} fill="url(#pipe-grad)"
          initial={{ scaleX: 0 }} whileInView={{ scaleX: 1 }} viewport={{ once: true }}
          style={{ transformOrigin: "42px 156px" }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
        />

        {/* Travelling packet across the full pipe */}
        <motion.circle r={4} fill="#334155"
          style={{ filter: "drop-shadow(0 0 5px #64748b)" }}
          animate={{ cx: [42, 552], cy: [156, 156], opacity: [0, 1, 1, 0] }}
          transition={{ duration: 2.4, repeat: Infinity, repeatDelay: 0.8, ease: "easeInOut" }}
        />

        {/* Nodes */}
        {nodes.map((n, i) => (
          <g key={n.label}>
            {/* Outer ring pulse */}
            <motion.circle cx={n.cx} cy={156} r={38}
              fill="none" stroke={n.color} strokeWidth={0.5} strokeOpacity={0.2}
              animate={{ r: [38, 46, 38], opacity: [0.2, 0.05, 0.2] }}
              transition={{ duration: 2.4, repeat: Infinity, delay: i * 0.4, ease: "easeInOut" }}
            />
            {/* Main circle */}
            <motion.circle cx={n.cx} cy={156} r={30}
              fill={`${n.color}15`} stroke={n.color} strokeWidth={1.5} strokeOpacity={0.8}
              style={{ filter: `drop-shadow(0 0 10px ${n.color}50)` }}
              initial={{ scale: 0, opacity: 0 }}
              whileInView={{ scale: 1, opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.18, duration: 0.5, type: "spring" }}
            />
            <text x={n.cx} y={152} textAnchor="middle" fontSize={8}
              fill={n.color} fontFamily="monospace" fontWeight="700">{n.label}</text>
            <text x={n.cx} y={165} textAnchor="middle" fontSize={6.5}
              fill={n.color} fontFamily="monospace" opacity={0.7}>{n.sub}</text>
          </g>
        ))}

        {/* Brief detail callout */}
        <motion.line x1={346} y1={188} x2={346} y2={205}
          stroke="#d97706" strokeWidth={1} strokeOpacity={0.5} strokeDasharray="3 2"
          initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}
          transition={{ delay: 1.0 }}
        />
        <motion.rect x={256} y={206} width={180} height={70} rx={8}
          fill="white" stroke="#f59e0b" strokeWidth={1} strokeOpacity={0.6}
          style={{ filter: "drop-shadow(0 4px 12px rgba(0,0,0,0.08))" }}
          initial={{ opacity: 0, y: 8 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
          transition={{ delay: 1.1 }}
        />
        <text x={346} y={223} textAnchor="middle" fontSize={7} fill="#d97706"
          fontFamily="monospace" fontWeight="800">DISPATCH PACKAGE</text>
        <text x={346} y={237} textAnchor="middle" fontSize={6.5} fill="#475569"
          fontFamily="monospace">Sector 7B · 28.5750°N 77.2500°E</text>
        <text x={346} y={249} textAnchor="middle" fontSize={6.5} fill="#475569"
          fontFamily="monospace">Severity 5/5 · Subgrade wash-out</text>
        <text x={346} y={261} textAnchor="middle" fontSize={6.5} fill="#475569"
          fontFamily="monospace">Confidence 87% · Evidence chain: 4 hops</text>

        <text x={295} y={300} textAnchor="middle" fontSize={7.5}
          fill="#94a3b8" fontFamily="monospace">
          Coordinates · history · causal chain → dispatched to field officer
        </text>
      </svg>
    </div>
  );
}

const steps = [
  {
    n: "01",
    title: "Omniscient Ingestion",
    tag: "Signal Layer",
    body: "Polaris integrates directly with existing SCADA systems, traffic sensors, IoT meters, and citizen reporting apps to compose a single real-time substrate of civic signal.",
    diagram: <IngestionDiagram />,
    color: "#3b82f6",
  },
  {
    n: "02",
    title: "Correlation Engine",
    tag: "Synthesis Agent",
    body: "Autonomous agents reason across domains. A reported water leak adjacent to an electrical substation is automatically escalated, weighted, and routed to the responsible team.",
    diagram: <CorrelationDiagram />,
    color: "#a855f7",
  },
  {
    n: "03",
    title: "Predictive Dispatch",
    tag: "Brief Agent",
    body: "Polaris forecasts infrastructure failures before they surface. Dispatch packages arrive in the field with full evidentiary context — coordinates, history, and confidence.",
    diagram: <DispatchDiagram />,
    color: "#f59e0b",
  },
];

export function Process() {
  return (
    <section id="process" className="relative py-32 border-t border-border-subtle bg-paper">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-16">

          {/* Sticky sidebar */}
          <div className="md:col-span-4">
            <div className="md:sticky md:top-32">
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-100px" }}
                transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                className="text-[11px] font-mono font-medium text-accent uppercase tracking-[0.22em] mb-5"
              >
                The Process
              </motion.div>
              <motion.h3
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-100px" }}
                transition={{ duration: 0.9, delay: 0.05, ease: [0.16, 1, 0.3, 1] }}
                className="font-display font-extrabold tracking-[-0.03em] text-4xl md:text-[2.75rem] leading-[1.05] mb-6 text-balance"
              >
                Fragmented data, unified intelligence.
              </motion.h3>
              <p className="text-slate-muted leading-relaxed text-pretty max-w-sm">
                Most cities operate in silos. Polaris bridges the gap between
                infrastructure hardware and civic decision-making through
                high-fidelity AI agents.
              </p>

              <div className="mt-10 hairline-x" />

              {/* Step nav */}
              <div className="mt-8 space-y-3">
                {steps.map((s) => (
                  <div key={s.n} className="flex items-center gap-3">
                    <div className="size-1.5 rounded-full" style={{ background: s.color }} />
                    <span className="font-mono text-[11px] text-slate-muted">
                      <span style={{ color: s.color }}>{s.n}</span> · {s.title}
                    </span>
                  </div>
                ))}
              </div>

              <div className="mt-8 font-mono text-[11px] text-slate-muted space-y-1.5 pt-6 border-t border-border-subtle">
                <div>03 · stages</div>
                <div>04 · agent classes</div>
                <div>∞ · signals/sec</div>
              </div>
            </div>
          </div>

          {/* Stage articles */}
          <div className="md:col-span-8 space-y-24">
            {steps.map((s, i) => (
              <motion.article
                key={s.n}
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-80px" }}
                transition={{ duration: 0.9, delay: i * 0.05, ease: [0.16, 1, 0.3, 1] }}
              >
                {/* Stage header */}
                <div className="flex items-center gap-4 mb-5">
                  <div
                    className="inline-flex items-center gap-2 px-3 py-1 rounded-full font-mono text-[10px] uppercase tracking-widest"
                    style={{ background: `${s.color}12`, color: s.color, border: `1px solid ${s.color}30` }}
                  >
                    <span>{s.n}</span>
                    <span className="opacity-40">·</span>
                    <span>{s.tag}</span>
                  </div>
                  <h4 className="text-xl md:text-2xl font-semibold tracking-tight">{s.title}</h4>
                </div>

                {/* Diagram panel — dark, rounded, with subtle glow border */}
                <div
                  className="relative w-full aspect-video rounded-2xl overflow-hidden mb-6 shadow-[0_0_0_1px_rgba(255,255,255,0.06),0_20px_60px_-20px_rgba(0,0,0,0.4)]"
                  style={{ boxShadow: `0 0 0 1px ${s.color}20, 0 20px 60px -20px rgba(0,0,0,0.5), 0 0 40px -20px ${s.color}15` }}
                >
                  {s.diagram}
                </div>

                {/* Body text */}
                <p className="text-slate-muted leading-relaxed max-w-lg text-pretty">
                  {s.body}
                </p>
              </motion.article>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
