import { motion } from "framer-motion";
import type { ReactNode } from "react";

export function PageTransition({ children }: { children: ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
    >
      {children}
    </motion.div>
  );
}

export function PageEyebrow({ kicker, title, lede }: { kicker: string; title: string; lede?: string }) {
  return (
    <header className="max-w-3xl">
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7 }}
        className="text-[11px] font-mono uppercase tracking-[0.22em] text-accent mb-5"
      >
        {kicker}
      </motion.div>
      <motion.h1
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
        className="font-display font-extrabold tracking-[-0.035em] leading-[1.02] text-[clamp(2.25rem,5vw,4rem)] text-balance"
      >
        {title}
      </motion.h1>
      {lede && (
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
          className="mt-6 text-lg text-slate-muted leading-relaxed max-w-2xl text-pretty"
        >
          {lede}
        </motion.p>
      )}
    </header>
  );
}
