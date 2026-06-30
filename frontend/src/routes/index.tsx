import { createFileRoute } from "@tanstack/react-router";
import { Nav } from "@/components/polaris/Nav";
import { Hero } from "@/components/polaris/Hero";
import { Process } from "@/components/polaris/Process";
import { AgentLog } from "@/components/polaris/AgentLog";
import { Metrics } from "@/components/polaris/Metrics";
import { OfficerCommand } from "@/components/polaris/OfficerCommand";
import { Footer } from "@/components/polaris/Footer";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Polaris — The Operating System for the Modern City" },
      {
        name: "description",
        content:
          "Polaris unifies fragmented urban infrastructure into a single autonomous intelligence layer. Predict failures, automate response, build resilient civic futures.",
      },
      {
        property: "og:title",
        content: "Polaris — The Operating System for the Modern City",
      },
      {
        property: "og:description",
        content:
          "The autonomous intelligence layer for modern cities. Citizen signal, AI agents, and officer dispatch — unified.",
      },
      { property: "og:type", content: "website" },
    ],
  }),
  component: Index,
});

function Index() {
  return (
    <div className="min-h-screen bg-canvas text-obsidian">
      <Nav />
      <main>
        <Hero />
        <Process />
        <AgentLog />
        <OfficerCommand />
        <Metrics />
      </main>
      <Footer />
    </div>
  );
}
