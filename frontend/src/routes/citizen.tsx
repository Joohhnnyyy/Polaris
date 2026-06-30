import { createFileRoute } from "@tanstack/react-router";
import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { Nav } from "@/components/polaris/Nav";
import { Footer } from "@/components/polaris/Footer";
import { PageEyebrow, PageTransition } from "@/components/polaris/PageTransition";
import { API_URL, WS_URL } from "@/lib/api";

export const Route = createFileRoute("/citizen")({
  head: () => ({
    meta: [
      { title: "Citizen Portal — Polaris" },
      {
        name: "description",
        content:
          "Report civic issues with live AI analysis, geolocation, media intake, and real-time agent processing — every signal escalated with full context.",
      },
      { property: "og:title", content: "Polaris Citizen Portal" },
      {
        property: "og:description",
        content:
          "Report a civic issue and watch Polaris reason about it in real time.",
      },
    ],
  }),
  component: CitizenPage,
});

const categories = [
  "Water · Pressure",
  "Power · Outage",
  "Roadway · Hazard",
  "Lighting · Failure",
  "Sanitation · Overflow",
  "Other",
];

const timeline = [
  { t: "T+00s", k: "Submission received", v: "Encrypted · ID_882041" },
  { t: "T+01s", k: "Geofence resolved", v: "District 04 · Block 19-A" },
  { t: "T+02s", k: "Media analysis", v: "Computer vision: water pooling · 0.91" },
  { t: "T+04s", k: "Correlating subsystem", v: "Pressure delta on Main-14 · Δ42psi" },
  { t: "T+06s", k: "Agent verdict", v: "Probable upstream failure · L3" },
  { t: "T+07s", k: "Dispatch package", v: "Unit-12 · ETA 11 min" },
];

function CitizenPage() {
  const [category, setCategory] = useState(categories[0]);
  const [desc, setDesc] = useState("Heavy water leak and bubbling road deformation observed near main lane.");
  const [lat, setLat] = useState("28.6850");
  const [lng, setLng] = useState("77.4800");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [filePreview, setFilePreview] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [trackingId, setTrackingId] = useState<string | null>(null);
  const [logs, setLogs] = useState<Array<{ id: string; text: string }>>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Connect to live WebSocket stream for real-time agent reasoning steps
  useEffect(() => {
    if (typeof window !== "undefined" && "geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLat(position.coords.latitude.toFixed(4));
          setLng(position.coords.longitude.toFixed(4));
        },
        (error) => {
          console.warn("Geolocation error/denied, defaulting to fallback:", error);
        }
      );
    }

    const ws = new WebSocket(`${WS_URL}/ws/logs`);
    
    ws.onmessage = (event) => {
      setLogs((prev) => [...prev, { id: Math.random().toString(), text: event.data }]);
    };

    return () => {
      ws.close();
    };
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setFilePreview(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async () => {
    if (isSubmitting) return;
    setIsSubmitting(true);
    setSubmitted(true);

    try {
      const formData = new FormData();
      formData.append("lat", lat);
      formData.append("lng", lng);
      formData.append("description", `[${category}] ${desc}`);

      if (selectedFile) {
        formData.append("image", selectedFile);
      } else {
        // Fallback demo blob if user didn't pick a file
        const res = await fetch("https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=800&auto=format&fit=crop");
        const blob = await res.blob();
        formData.append("image", blob, "report.jpg");
      }

      const response = await fetch(`${API_URL}/reports`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (data.success && data.issue_id) {
        setTrackingId(data.issue_id);
      }
    } catch (err) {
      console.error("Submission failed:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <PageTransition>
      <div className="min-h-screen bg-canvas text-obsidian">
        <Nav />
        <main className="pt-32 pb-24">
          <div className="max-w-7xl mx-auto px-6">
            <PageEyebrow
              kicker="Citizen Portal · 01"
              title="The city listens. Then it acts."
              lede="A single signal from any resident is enough. Polaris fuses your report with sensor data, prior history, and ongoing operations — and routes a response within seconds."
            />

            <div className="mt-20 grid grid-cols-1 lg:grid-cols-12 gap-10">
              {/* Form */}
              <section className="lg:col-span-7">
                <div className="rounded-2xl border border-border-subtle bg-paper p-8 md:p-10 shadow-[0_24px_80px_-60px_rgba(9,9,11,0.35)]">
                  <div className="flex items-center justify-between mb-8">
                    <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-slate-muted">
                      report.intake / live-connected
                    </div>
                    <div className="font-mono text-[10px] text-accent">v4.0</div>
                  </div>

                  <Field label="What's happening?">
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                      {categories.map((c) => (
                        <button
                          key={c}
                          type="button"
                          onClick={() => setCategory(c)}
                          className={`text-left px-3.5 py-2.5 rounded-lg border text-[12px] font-mono uppercase tracking-tight transition-all ${
                            category === c
                              ? "border-accent bg-accent-soft text-accent"
                              : "border-border-subtle bg-canvas text-slate-muted hover:border-border-strong"
                          }`}
                        >
                          {c}
                        </button>
                      ))}
                    </div>
                  </Field>

                  <Field label="Describe what you're seeing">
                    <textarea
                      value={desc}
                      onChange={(e) => setDesc(e.target.value)}
                      rows={4}
                      className="w-full resize-none rounded-lg border border-border-subtle bg-canvas p-4 text-[14px] leading-relaxed focus:outline-none focus:border-accent transition-colors"
                    />
                  </Field>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Field label="Geolocation (LAT, LNG)" mono>
                      <div className="px-4 py-3 rounded-lg border border-border-subtle bg-canvas font-mono text-[12px] flex items-center justify-between gap-2">
                        <input 
                          type="text" 
                          value={`${lat}, ${lng}`} 
                          onChange={(e) => {
                            const parts = e.target.value.split(",");
                            if (parts[0]) setLat(parts[0].trim());
                            if (parts[1]) setLng(parts[1].trim());
                          }}
                          className="bg-transparent border-none focus:outline-none w-full font-mono"
                        />
                        <span className="size-1.5 rounded-full bg-accent animate-pulse shrink-0" />
                      </div>
                    </Field>

                    <Field label="Media intake (Image)" mono>
                      <input 
                        type="file" 
                        ref={fileInputRef} 
                        onChange={handleFileChange} 
                        accept="image/*" 
                        className="hidden" 
                      />
                      <button 
                        type="button"
                        onClick={() => fileInputRef.current?.click()}
                        className="w-full text-left px-4 py-3 rounded-lg border border-dashed border-border-strong bg-canvas font-mono text-[12px] text-slate-muted flex items-center justify-between hover:border-accent transition-colors"
                      >
                        <span className="truncate">
                          {selectedFile ? selectedFile.name : "Attach photo..."}
                        </span>
                        <span className="text-accent shrink-0">+ upload</span>
                      </button>
                    </Field>
                  </div>

                  {filePreview && (
                    <div className="mt-4 rounded-lg overflow-hidden border border-border-subtle max-h-48">
                      <img src={filePreview} alt="Upload preview" className="w-full h-full object-cover" />
                    </div>
                  )}

                  <div className="mt-8 flex items-center justify-between">
                    <div className="font-mono text-[10px] text-slate-muted">
                      Live Backend Connected · FastAPI 8000
                    </div>
                    <button
                      type="button"
                      onClick={handleSubmit}
                      disabled={submitted}
                      className="inline-flex items-center gap-2 px-6 py-3 bg-obsidian text-canvas text-[13px] font-medium rounded-full hover:opacity-90 transition disabled:opacity-50"
                    >
                      {submitted ? (isSubmitting ? "Processing Agent Cortex..." : "Report Dispatched") : "Submit to Polaris"}
                      <span>→</span>
                    </button>
                  </div>
                </div>
              </section>

              {/* Live processing */}
              <aside className="lg:col-span-5">
                <div className="rounded-2xl border border-border-subtle bg-obsidian text-canvas overflow-hidden">
                  <div className="flex items-center justify-between px-5 py-3 border-b border-white/10">
                    <div className="flex items-center gap-2">
                      <span className="size-1.5 rounded-full bg-accent animate-pulse" />
                      <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-white/60">
                        agent.intake / websocket stream
                      </span>
                    </div>
                    <span className="font-mono text-[10px] text-accent">{WS_URL}</span>
                  </div>
                  <div className="p-6 min-h-[420px] max-h-[520px] overflow-y-auto">
                    {logs.length === 0 ? (
                      <div className="h-full flex flex-col items-start justify-center text-white/40 font-mono text-[12px] gap-3 pt-24">
                        <span>// awaiting submission…</span>
                        <span>// agents standing by · 4 multi-agent cortex active</span>
                      </div>
                    ) : (
                      <ol className="space-y-4 font-mono text-[12px]">
                        <AnimatePresence>
                          {logs.map((log) => (
                            <motion.li
                              key={log.id}
                              initial={{ opacity: 0, x: -8 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ duration: 0.3 }}
                              className="text-white/80 leading-relaxed border-l-2 border-accent/40 pl-3 py-1 bg-white/[0.02] rounded-r"
                            >
                              {log.text}
                            </motion.li>
                          ))}
                        </AnimatePresence>
                      </ol>
                    )}
                  </div>
                  {trackingId && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="px-6 py-4 border-t border-white/10 bg-accent/10 text-[12px]"
                    >
                      Tracking ID <span className="font-mono text-accent">{trackingId}</span> · Saved to Supabase.
                    </motion.div>
                  )}
                </div>

                <div className="mt-5 grid grid-cols-3 gap-px bg-border-subtle border border-border-subtle rounded-xl overflow-hidden">
                  {[
                    ["Median triage", "04s"],
                    ["Agent Cortex", "Gemini 2.5"],
                    ["Auto-resolved", "89%"],
                  ].map(([k, v]) => (
                    <div key={k} className="bg-paper p-4">
                      <div className="font-mono text-[9px] text-slate-muted uppercase tracking-widest">
                        {k}
                      </div>
                      <div className="mt-1 font-display font-extrabold text-lg tracking-tight">
                        {v}
                      </div>
                    </div>
                  ))}
                </div>
              </aside>
            </div>
          </div>
        </main>
        <Footer />
      </div>
    </PageTransition>
  );
}

function Field({ label, children, mono }: { label: string; children: React.ReactNode; mono?: boolean }) {
  return (
    <div className="mb-6">
      <div className={`text-[10px] uppercase tracking-[0.2em] text-slate-muted mb-2.5 ${mono ? "font-mono" : "font-mono"}`}>
        {label}
      </div>
      {children}
    </div>
  );
}
