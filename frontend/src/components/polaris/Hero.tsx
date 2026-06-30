import { motion, useScroll, useTransform, useMotionValue, useSpring } from "framer-motion";
import { useRef, useEffect, useState } from "react";
import heroCity from "@/assets/hero-city.jpg";
import { API_URL } from "@/lib/api";

const words = ["The", "intelligence", "layer", "for", "the", "modern", "city."];

export function Hero() {
  const ref = useRef<HTMLDivElement>(null);
  const [issueCount, setIssueCount] = useState<number | null>(null);
  const [clusterCount, setClusterCount] = useState<number | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/issues`).then((r) => r.json()).then((d) => setIssueCount(d.length)).catch(() => {});
    fetch(`${API_URL}/clusters`).then((r) => r.json()).then((d) => setClusterCount(d.length)).catch(() => {});
  }, []);

  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end start"],
  });
  const imgY = useTransform(scrollYProgress, [0, 1], ["0%", "18%"]);
  const imgScale = useTransform(scrollYProgress, [0, 1], [1, 1.08]);
  const overlayOpacity = useTransform(scrollYProgress, [0, 0.7], [0, 0.6]);
  const heroFade = useTransform(scrollYProgress, [0, 0.6], [1, 0]);

  // Global window mouse movement tracking spring values with super smooth motion
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const springConfig = { damping: 40, stiffness: 60 };
  const moveX = useSpring(useTransform(mouseX, [-0.5, 0.5], [-60, 60]), springConfig);
  const moveY = useSpring(useTransform(mouseY, [-0.5, 0.5], [-60, 60]), springConfig);
  const rotateX = useSpring(useTransform(mouseY, [-0.5, 0.5], [18, -18]), springConfig);
  const rotateY = useSpring(useTransform(mouseX, [-0.5, 0.5], [-18, 18]), springConfig);

  useEffect(() => {
    const handleGlobalMouseMove = (e: MouseEvent) => {
      const x = e.clientX / window.innerWidth - 0.5;
      const y = e.clientY / window.innerHeight - 0.5;
      mouseX.set(x);
      mouseY.set(y);
    };

    window.addEventListener("mousemove", handleGlobalMouseMove);
    return () => window.removeEventListener("mousemove", handleGlobalMouseMove);
  }, [mouseX, mouseY]);

  return (
    <section 
      ref={ref} 
      className="relative pt-32 pb-24 overflow-hidden min-h-[85vh] flex flex-col justify-center"
    >
      <motion.div 
        style={{ x: moveX, y: moveY, rotateX, rotateY, perspective: 1000 }}
        className="spline-container absolute -top-2 md:-top-8 -right-6 md:-right-10 lg:-right-16 w-[500px] md:w-[650px] lg:w-[750px] h-[500px] md:h-[650px] lg:h-[750px] z-20 pointer-events-none flex items-center justify-center opacity-90 scale-65 md:scale-75 lg:scale-80 origin-center"
      >
        <div 
          className="w-full h-full rounded-full overflow-hidden pointer-events-none"
          style={{
            maskImage: 'radial-gradient(circle at 50% 50%, rgba(0, 0, 0, 1) 25%, rgba(0, 0, 0, 0.8) 45%, rgba(0, 0, 0, 0) 68%)',
            WebkitMaskImage: 'radial-gradient(circle at 50% 50%, rgba(0, 0, 0, 1) 25%, rgba(0, 0, 0, 0.8) 45%, rgba(0, 0, 0, 0) 68%)'
          }}
        >
          <iframe
            src="https://my.spline.design/celestialflowabstractdigitalform-ObUlVgj70g2y4bbx5vBKSfxN/"
            frameBorder="0"
            width="100%"
            height="100%"
            className="w-full h-full pointer-events-none"
            id="aura-spline"
          />
        </div>
      </motion.div>
      <div className="absolute inset-0 grid-pattern opacity-[0.25] pointer-events-none [mask-image:radial-gradient(ellipse_at_top,black,transparent_75%)] z-0" />

      <div className="max-w-7xl mx-auto px-6 relative z-10 w-full">
        <motion.div style={{ opacity: heroFade }} className="max-w-3xl">
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-border-subtle bg-paper text-[11px] font-mono tracking-tight mb-10"
          >
            <span className="text-accent">●</span>
            <span className="text-slate-muted">VERSION 4.0 —</span>
            <span>URBAN OPERATING SYSTEM</span>
          </motion.div>

          <h1 className="font-display font-extrabold tracking-[-0.035em] leading-[1.02] text-balance text-[clamp(2.75rem,7vw,5.5rem)] mb-10">
            {words.map((w, i) => (
              <motion.span
                key={i}
                initial={{ y: "110%", opacity: 0 }}
                animate={{ y: "0%", opacity: 1 }}
                transition={{
                  duration: 0.9,
                  delay: 0.15 + i * 0.06,
                  ease: [0.16, 1, 0.3, 1],
                }}
                className={`inline-block mr-[0.22em] ${
                  w === "modern" || w === "city." ? "text-accent" : ""
                }`}
                style={{
                  // wrap each word so its slide-up clips behind a hidden mask
                  overflow: "hidden",
                }}
              >
                {w}
              </motion.span>
            ))}
          </h1>

          <motion.p
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, delay: 0.7, ease: [0.16, 1, 0.3, 1] }}
            className="text-lg md:text-xl text-slate-muted leading-relaxed max-w-xl mb-12 text-pretty"
          >
            Polaris unifies fragmented urban infrastructure into a single,
            cohesive neural network. Predict failures, automate response, and
            build resilient civic futures.
          </motion.p>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.9, delay: 0.85 }}
            className="flex flex-wrap items-center gap-6"
          >
            <a
              href="#process"
              className="group inline-flex items-center gap-2 text-sm font-semibold"
            >
              Explore the architecture
              <span className="inline-block transition-transform group-hover:translate-x-1">
                →
              </span>
            </a>
            <span className="h-px w-12 bg-border-strong" />
            <span className="text-[12px] text-slate-muted font-mono tracking-tight">
              LAT 40.7128 · LONG −74.0060
            </span>
          </motion.div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.1, delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
          className="mt-24 relative"
        >
          <div className="absolute -top-16 -left-16 size-64 rounded-full bg-accent/[0.06] blur-3xl pointer-events-none" />
          <div className="relative w-full aspect-[21/9] bg-paper border border-border-subtle rounded-2xl overflow-hidden shadow-[0_30px_80px_-40px_rgba(9,9,11,0.18)]">
            <motion.img
              src={heroCity}
              alt="Polaris live city digital twin visualization"
              width={1920}
              height={1024}
              style={{ y: imgY, scale: imgScale }}
              className="absolute inset-0 size-full object-cover"
            />
            <motion.div
              style={{ opacity: overlayOpacity }}
              className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-canvas"
            />
            <div className="absolute inset-0 grid-pattern opacity-[0.18] mix-blend-multiply" />

            {/* Telemetry HUD */}
            <div className="absolute top-5 left-5 flex items-center gap-2 px-2.5 py-1.5 rounded-md glass border border-border-subtle">
              <span className="size-1.5 rounded-full bg-accent animate-pulse" />
              <span className="font-mono text-[10px] tracking-[0.16em] uppercase">
                Live · {issueCount !== null ? `${issueCount} Incidents` : "Connecting…"}
              </span>
            </div>
            <div className="absolute bottom-5 right-5 grid grid-cols-3 gap-px bg-border-subtle border border-border-subtle rounded-md overflow-hidden text-[10px] font-mono">
              {[
                ["Incidents", issueCount !== null ? issueCount.toLocaleString() : "…"],
                ["Clusters", clusterCount !== null ? clusterCount.toString() : "…"],
                ["Uptime", "99.99%"],
              ].map(([k, v]) => (
                <div key={k} className="bg-paper px-3 py-2">
                  <div className="text-slate-muted uppercase tracking-widest text-[9px]">{k}</div>
                  <div className="text-obsidian">{v}</div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
