import { createFileRoute } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { Nav } from "@/components/polaris/Nav";
import { PageTransition } from "@/components/polaris/PageTransition";
import { API_URL, WS_URL } from "@/lib/api";

export const Route = createFileRoute("/map")({
  head: () => ({
    meta: [
      { title: "Urban Intelligence Map — Polaris" },
      {
        name: "description",
        content:
          "A full-screen GIS workspace with animated infrastructure layers, predictive heatmaps, cluster visualization, and timeline playback.",
      },
      { property: "og:title", content: "Polaris Urban Intelligence Map" },
      {
        property: "og:description",
        content: "Predictive geospatial intelligence at city scale.",
      },
    ],
  }),
  component: MapPage,
});

const darkMapStyles = [
  { elementType: "geometry", stylers: [{ color: "#0c0d12" }] },
  { elementType: "labels.text.stroke", stylers: [{ color: "#0c0d12" }] },
  { elementType: "labels.text.fill", stylers: [{ color: "#7f8497" }] },
  {
    featureType: "administrative.locality",
    elementType: "labels.text.fill",
    stylers: [{ color: "#a855f7" }],
  },
  {
    featureType: "poi",
    stylers: [{ visibility: "off" }],
  },
  {
    featureType: "road",
    elementType: "geometry",
    stylers: [{ color: "#181a23" }],
  },
  {
    featureType: "road",
    elementType: "geometry.stroke",
    stylers: [{ color: "#252836" }],
  },
  {
    featureType: "road",
    elementType: "labels.text.fill",
    stylers: [{ color: "#6b7280" }],
  },
  {
    featureType: "road.highway",
    elementType: "geometry",
    stylers: [{ color: "#252836" }],
  },
  {
    featureType: "road.highway",
    elementType: "geometry.stroke",
    stylers: [{ color: "#374151" }],
  },
  {
    featureType: "water",
    elementType: "geometry",
    stylers: [{ color: "#080c16" }],
  },
  {
    featureType: "water",
    elementType: "labels.text.fill",
    stylers: [{ color: "#3b82f6" }],
  },
];

function MapPage() {
  const [apiKey, setApiKey] = useState("");
  const [mapLoaded, setMapLoaded] = useState(false);
  const [issues, setIssues] = useState<any[]>([]);
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [selectedIssue, setSelectedIssue] = useState<any | null>(null);
  const setSelectedIssueRef = { current: setSelectedIssue };

  // Fetch API key from backend Config
  useEffect(() => {
    fetch(`${API_URL}/config`)
      .then((res) => res.json())
      .then((data) => {
        if (data.google_maps_key) {
          setApiKey(data.google_maps_key);
        }
      })
      .catch((err) => console.error("Failed to load map config:", err));
  }, []);

  const fetchIssues = () => {
    fetch(`${API_URL}/issues`)
      .then((res) => res.json())
      .then((data) => setIssues(data))
      .catch((err) => console.error("Failed to fetch live issues:", err));
  };

  // Fetch live issues
  useEffect(() => {
    fetchIssues();

    // Live Sync via WebSocket
    const ws = new WebSocket(`${WS_URL}/ws/logs`);
    ws.onmessage = () => {
      fetchIssues();
    };

    return () => {
      ws.close();
    };
  }, []);

  // Load Google Maps script
  useEffect(() => {
    if (!apiKey) return;
    if ((window as any).google?.maps) {
      setMapLoaded(true);
      return;
    }
    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=geometry`;
    script.async = true;
    script.defer = true;
    script.onload = () => setMapLoaded(true);
    document.head.appendChild(script);
  }, [apiKey]);

  // Initialize Map and Markers
  useEffect(() => {
    if (!mapLoaded || !apiKey) return;
    const mapEl = document.getElementById("google-map-canvas");
    if (!mapEl) return;

    // Center Noida grid coordinates
    const noidaCenter = { lat: 28.585, lng: 77.29 };
    const map = new (window as any).google.maps.Map(mapEl, {
      center: noidaCenter,
      zoom: 13,
      styles: darkMapStyles,
      disableDefaultUI: true,
      zoomControl: true,
    });

    const filteredIssues = activeCategory
      ? issues.filter((i) => i.category === activeCategory)
      : issues;

    const colorMap: Record<string, string> = {
      "Water Leak": "#3b82f6",
      "Pothole": "#f43f5e",
      "Garbage Pile": "#10b981",
      "Pavement Subsidence": "#a855f7",
      "Broken Streetlight": "#eab308",
    };

    // Render Markers
    filteredIssues.forEach((issue) => {
      if (!issue.lat || !issue.lng) return;
      const markerColor = colorMap[issue.category] || "#9ca3af";

      const marker = new (window as any).google.maps.Marker({
        position: { lat: Number(issue.lat), lng: Number(issue.lng) },
        map: map,
        title: issue.category,
        icon: {
          path: (window as any).google.maps.SymbolPath.CIRCLE,
          scale: 8,
          fillColor: markerColor,
          fillOpacity: 0.9,
          strokeColor: "#ffffff",
          strokeWeight: 1.5,
        },
      });

      marker.addListener("click", () => {
        setSelectedIssueRef.current(issue);
      });
    });
  }, [mapLoaded, apiKey, issues, activeCategory]);

  return (
    <PageTransition>
      <div className="min-h-screen bg-obsidian text-canvas">
        <Nav />
        <div className="h-screen pt-16 flex">
          {/* Left sidebar */}
          <aside className="w-72 shrink-0 border-r border-white/[0.06] bg-obsidian flex flex-col">
            <div className="p-5 border-b border-white/[0.06]">
              <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-accent">
                GIS Workstation
              </div>
              <h1 className="mt-2 font-display font-extrabold text-2xl tracking-tight leading-tight">
                Live Google Map
              </h1>
              <p className="mt-3 text-[12px] text-white/50 leading-relaxed">
                Geospatial substrate displaying Noida grid coordinates and active civic incidents.
              </p>
            </div>

            <div className="p-5 border-b border-white/[0.06]">
              <div className="font-mono text-[10px] uppercase tracking-[0.18em] text-white/40 mb-3">
                Category Filters
              </div>
              <ul className="space-y-1">
                {[
                  { label: "All Incidents", value: null, color: "#a855f7" },
                  { label: "Water Leaks", value: "Water Leak", color: "#3b82f6" },
                  { label: "Potholes", value: "Pothole", color: "#f43f5e" },
                  { label: "Garbage Piles", value: "Garbage Pile", color: "#10b981" },
                  { label: "Pavement Subsidence", value: "Pavement Subsidence", color: "#a855f7" },
                  { label: "Broken Streetlights", value: "Broken Streetlight", color: "#eab308" },
                ].map((f, i) => (
                  <li key={i}>
                    <button
                      onClick={() => setActiveCategory(f.value)}
                      className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-[12px] transition-colors ${
                        activeCategory === f.value ? "bg-white/[0.06] text-canvas font-semibold" : "text-white/50 hover:bg-white/[0.03]"
                      }`}
                    >
                      <span className="size-2 rounded-full" style={{ background: f.color }} />
                      <span className="flex-1 text-left">{f.label}</span>
                    </button>
                  </li>
                ))}
              </ul>
            </div>

            <div className="mt-auto p-5 font-mono text-[10px] text-white/40">
              System: Synced Live<br />Google Maps Workspace
            </div>
          </aside>

          {/* Map canvas */}
          <div className="flex-1 relative bg-[#06070b]">
            <div id="google-map-canvas" className="w-full h-full" />

            {/* Floating Brief — Dynamic */}
            <div className="absolute top-6 right-6 w-[340px] p-5 rounded-xl border border-white/10 bg-obsidian/90 backdrop-blur transition-all">
              {selectedIssue ? (
                <>
                  <div className="flex items-center justify-between mb-3">
                    <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-accent">Incident Detail</span>
                    <button
                      onClick={() => setSelectedIssue(null)}
                      className="font-mono text-[10px] text-white/30 hover:text-white/70 transition"
                    >
                      ✕ close
                    </button>
                  </div>
                  <div
                    className="inline-block px-2 py-0.5 rounded font-mono text-[10px] uppercase tracking-wider font-bold mb-2"
                    style={{
                      background: ({
                        "Water Leak": "#3b82f620",
                        "Pothole": "#f43f5e20",
                        "Garbage Pile": "#10b98120",
                        "Pavement Subsidence": "#a855f720",
                        "Broken Streetlight": "#eab30820",
                      } as any)[selectedIssue.category] || "#ffffff10",
                      color: ({
                        "Water Leak": "#3b82f6",
                        "Pothole": "#f43f5e",
                        "Garbage Pile": "#10b981",
                        "Pavement Subsidence": "#a855f7",
                        "Broken Streetlight": "#eab308",
                      } as any)[selectedIssue.category] || "#9ca3af",
                    }}
                  >
                    {selectedIssue.category}
                  </div>
                  <div className="text-[16px] font-bold leading-snug">
                    Severity {selectedIssue.severity}/5
                    {selectedIssue.severity >= 4 && (
                      <span className="ml-2 text-rose-400 text-[11px] font-mono align-middle">● CRITICAL</span>
                    )}
                  </div>
                  <div className="mt-1 font-mono text-[10px] text-white/40">
                    {Number(selectedIssue.lat).toFixed(5)}°N, {Number(selectedIssue.lng).toFixed(5)}°E
                  </div>
                  <p className="mt-3 text-[12px] text-white/65 leading-relaxed border-t border-white/[0.06] pt-3">
                    {selectedIssue.description || "No description provided."}
                  </p>
                  <div className="mt-3 grid grid-cols-2 gap-2">
                    {[
                      ["Status", selectedIssue.status || "REPORTED"],
                      ["ID", selectedIssue.id?.slice(0, 8).toUpperCase()],
                      ["Reported", selectedIssue.created_at ? new Date(selectedIssue.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "—"],
                      ["Zone", "Sector 7B"],
                    ].map(([k, v]) => (
                      <div key={k} className="bg-white/[0.03] rounded-lg p-2">
                        <div className="font-mono text-[9px] uppercase tracking-widest text-white/30">{k}</div>
                        <div className="mt-0.5 text-[11px] font-semibold text-accent">{v}</div>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <>
                  <div className="flex items-center justify-between mb-3">
                    <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-accent">Geospatial Feed</span>
                    <span className="flex items-center gap-1.5 font-mono text-[10px] text-emerald-400">
                      <span className="size-1.5 rounded-full bg-emerald-400 animate-pulse inline-block" />
                      Live Sync
                    </span>
                  </div>
                  <div className="text-[14px] font-semibold leading-snug">
                    {activeCategory ? `${activeCategory} Events` : "All Active Incidents"}
                  </div>
                  <div className="mt-1 font-mono text-[11px] text-white/40">
                    {(activeCategory ? issues.filter(i => i.category === activeCategory) : issues).length} markers · Noida Municipal Grid
                  </div>
                  <div className="mt-3 grid grid-cols-2 gap-px bg-white/[0.05] rounded-lg overflow-hidden">
                    {Object.entries(
                      issues.reduce((acc: any, i) => {
                        acc[i.category] = (acc[i.category] || 0) + 1;
                        return acc;
                      }, {})
                    ).slice(0, 4).map(([cat, count]) => (
                      <div key={cat} className="bg-obsidian p-2.5">
                        <div className="font-mono text-[9px] uppercase text-white/30 truncate">{cat.split(" ")[0]}</div>
                        <div className="mt-0.5 text-[13px] font-bold text-canvas">{String(count)}</div>
                      </div>
                    ))}
                  </div>
                  <p className="mt-3 text-[11px] text-white/35 leading-relaxed">
                    Click any marker to inspect forensic details.
                  </p>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </PageTransition>
  );
}
