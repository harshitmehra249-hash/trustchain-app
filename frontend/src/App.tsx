import { Link, Route, Routes } from "react-router-dom";
import { useEffect, useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

function Home() {
  const [status, setStatus] = useState("Checking backend...");

  useEffect(() => {
    const controller = new AbortController();

    const load = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/health`, {
          signal: controller.signal,
        });
        if (!response.ok) {
          setStatus(`Backend responded with HTTP ${response.status}`);
          return;
        }
        const payload = (await response.json()) as { status?: string };
        setStatus(payload.status ?? "Backend is reachable");
      } catch {
        setStatus("Backend is not reachable. Start the backend service first.");
      }
    };

    void load();
    return () => controller.abort();
  }, []);

  return (
    <main style={{ fontFamily: "sans-serif", margin: "2rem auto", maxWidth: 840 }}>
      <h1>TrustChain</h1>
      <p>Decentralized disaster response network</p>
      <p>
        <strong>Backend status:</strong> {status}
      </p>
      <section>
        <h2>Core Modules</h2>
        <ul>
          <li>Mesh networking APIs for node heartbeat and message routing</li>
          <li>Supply-chain tracking with transfer history and QR generation</li>
          <li>AI-assisted request prioritization with offline-safe fallback</li>
          <li>Volunteer credentials and dashboard analytics endpoints</li>
        </ul>
      </section>
    </main>
  );
}

function NotFound() {
  return (
    <main style={{ fontFamily: "sans-serif", margin: "2rem auto", maxWidth: 840 }}>
      <h1>Page not found</h1>
      <p>
        Go back to the <Link to="/">home page</Link>.
      </p>
    </main>
  );
}

export function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
