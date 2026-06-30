import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Link, useRouterState } from "@tanstack/react-router";

const links = [
  { label: "Citizen", to: "/citizen" as const },
  { label: "Command", to: "/command" as const },
  { label: "Map", to: "/map" as const },
  { label: "Autopsy", to: "/autopsy" as const },
  { label: "Transparency", to: "/transparency" as const },
];

export function Nav() {
  const [scrolled, setScrolled] = useState(false);
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const onDark = pathname === "/command" || pathname === "/autopsy" || pathname === "/map";

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <motion.nav
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      className={`fixed top-0 inset-x-0 z-50 transition-[background,border-color,backdrop-filter] duration-500 ${
        onDark
          ? "bg-obsidian/70 backdrop-blur-md border-b border-white/[0.06]"
          : scrolled
            ? "glass border-b border-border-subtle"
            : "border-b border-transparent"
      }`}
    >
      <div className={`max-w-[1400px] mx-auto px-6 h-16 grid grid-cols-[auto_1fr_auto] items-center gap-8 ${onDark ? "text-canvas" : "text-obsidian"}`}>
        <Link to="/" className="flex items-center gap-2.5">
          <span className="size-1.5 rounded-full bg-accent" />
          <span className="font-display font-extrabold tracking-tight text-sm uppercase">
            Polaris
          </span>
        </Link>
        <div className="hidden md:flex items-center justify-center gap-7">
          {links.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              className={`text-[13px] font-medium transition-colors ${onDark ? "text-white/55 hover:text-white" : "text-slate-muted hover:text-obsidian"}`}
              activeProps={{ className: onDark ? "text-white" : "text-obsidian" }}
            >
              {l.label}
            </Link>
          ))}
        </div>
        <div className="flex items-center gap-3">
          <span className="hidden sm:inline-flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.18em] text-accent px-2.5 py-1 rounded-full bg-accent-soft">
            <span className="size-1.5 rounded-full bg-accent animate-pulse" />
            System Nominal
          </span>
          <Link
            to="/command"
            className={`px-4 py-2 text-[13px] font-medium rounded-full transition hover:opacity-90 ${onDark ? "bg-canvas text-obsidian" : "bg-obsidian text-canvas"}`}
          >
            Deploy Platform
          </Link>
        </div>
      </div>
    </motion.nav>
  );
}
