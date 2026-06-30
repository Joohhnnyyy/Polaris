import { motion, useInView } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { API_URL, safeFetchArray } from "@/lib/api";

function Counter({ to, decimals = 0, suffix = "" }: { to: number; decimals?: number; suffix?: string }) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-50px" });
  const [val, setVal] = useState(0);

  useEffect(() => {
    if (!inView) return;
    let raf = 0;
    const start = performance.now();
    const dur = 1400;
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / dur);
      const eased = 1 - Math.pow(1 - t, 3);
      setVal(to * eased);
      if (t < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [inView, to]);

  return (
    <span ref={ref} className="tabular-nums">
      {val.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}
      {suffix}
    </span>
  );
}

export function Metrics() {
  const [issues, setIssues] = useState<any[]>([]);
  const [clusters, setClusters] = useState<any[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    Promise.all([
      safeFetchArray(`${API_URL}/issues`),
      safeFetchArray(`${API_URL}/clusters`),
    ]).then(([iss, cls]) => {
      setIssues(iss);
      setClusters(cls);
      setLoaded(true);
    });
  }, []);

  const totalIssues = issues.length;
  const avgConfidence = clusters.length > 0
    ? Math.round(clusters.reduce((s, c) => s + (c.confidence || 0.7), 0) / clusters.length * 100)
    : 70;
  const resolvedCount = issues.filter((i) => i.status === "RESOLVED").length;

  const stats = [
    { value: loaded ? totalIssues : 0, suffix: "", label: "Live Incidents" },
    { value: loaded ? avgConfidence : 0, suffix: "%", label: "AI Confidence" },
    { value: loaded ? clusters.length : 0, suffix: "", label: "Active Clusters" },
    { value: loaded ? resolvedCount : 0, suffix: "", label: "Issues Resolved" },
  ];

  return (
    <section id="infrastructure" className="py-28 border-t border-border-subtle bg-canvas">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-border-subtle border border-border-subtle rounded-xl overflow-hidden">
          {stats.map((s, i) => (
            <motion.div
              key={s.label}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.7, delay: i * 0.08, ease: [0.16, 1, 0.3, 1] }}
              className="bg-paper p-8 md:p-10"
            >
              <div className="font-display font-extrabold tracking-[-0.03em] text-4xl md:text-5xl mb-3">
                <Counter to={s.value} suffix={s.suffix} />
              </div>
              <div className="text-[11px] font-mono uppercase tracking-[0.18em] text-slate-muted">{s.label}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
