import { motion } from "framer-motion";
import { Link } from "@tanstack/react-router";

export function Footer() {
  return (
    <footer
      id="transparency-footer"
      className="pt-28 pb-12 border-t border-border-subtle bg-canvas text-obsidian"
    >
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center">
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7 }}
            className="text-[11px] font-mono font-medium text-slate-muted uppercase tracking-[0.22em] mb-8"
          >
            Join the intelligence layer
          </motion.div>
          <motion.h2
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
            className="font-display font-extrabold tracking-[-0.035em] text-5xl md:text-[3.75rem] leading-[1.02] mb-12 text-balance max-w-3xl mx-auto"
          >
            The city of the future is an operating system.
          </motion.h2>
          <div className="flex flex-wrap justify-center gap-3">
            <Link
              to="/command"
              className="inline-flex items-center gap-2 px-6 py-3.5 bg-obsidian text-canvas text-sm font-medium rounded-full hover:opacity-90 transition"
            >
              Enter Command Center
              <span>→</span>
            </Link>
            <Link
              to="/autopsy"
              className="inline-flex items-center px-6 py-3.5 border border-border-strong text-sm font-medium rounded-full hover:bg-paper transition"
            >
              Open the Autopsy Studio
            </Link>
          </div>
        </div>

        <div className="mt-28 pt-10 border-t border-border-subtle grid grid-cols-2 md:grid-cols-4 gap-10">
          <div className="col-span-2 md:col-span-1">
            <Link to="/" className="flex items-center gap-2 mb-4">
              <span className="size-1.5 rounded-full bg-accent" />
              <span className="font-display font-extrabold tracking-tight text-sm uppercase">
                Polaris
              </span>
            </Link>
            <p className="text-[12px] text-slate-muted leading-relaxed max-w-[28ch]">
              The autonomous intelligence layer for modern civilization.
            </p>
          </div>
          <FooterCol
            title="Product"
            links={[
              { label: "Citizen Portal", to: "/citizen" },
              { label: "Command Center", to: "/command" },
              { label: "Intelligence Map", to: "/map" },
              { label: "Autopsy Studio", to: "/autopsy" },
            ]}
          />
          <FooterCol
            title="Public"
            links={[
              { label: "Transparency", to: "/transparency" },
              { label: "Manifesto", to: "/" },
              { label: "Engineering", to: "/" },
              { label: "Press", to: "/" },
            ]}
          />
          <FooterCol
            title="Legal"
            links={[
              { label: "Security", to: "/" },
              { label: "Privacy", to: "/" },
              { label: "Compliance", to: "/" },
              { label: "Contact", to: "/" },
            ]}
          />
        </div>

        <div className="mt-12 pt-6 border-t border-border-subtle flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="text-[10px] font-mono uppercase tracking-[0.22em] text-slate-muted">
            Polaris © 2026 · All systems nominal
          </div>
          <div className="font-mono text-[10px] text-slate-muted">
            v4.0.142 · build a8f23e1
          </div>
        </div>
      </div>
    </footer>
  );
}

type RoutePath = "/" | "/citizen" | "/command" | "/map" | "/autopsy" | "/transparency";

function FooterCol({
  title,
  links,
}: {
  title: string;
  links: { label: string; to: RoutePath }[];
}) {
  return (
    <div>
      <div className="text-[10px] font-mono uppercase tracking-[0.22em] text-slate-muted mb-4">
        {title}
      </div>
      <ul className="space-y-2.5">
        {links.map((l) => (
          <li key={l.label}>
            <Link
              to={l.to}
              className="text-[13px] text-obsidian hover:text-accent transition-colors"
            >
              {l.label}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
