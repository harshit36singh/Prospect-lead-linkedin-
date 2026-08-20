import { useEffect, useState } from "react";
import { api } from "./api/client";
import { IcpListPage } from "./pages/IcpListPage";
import { IcpFormPage } from "./pages/IcpFormPage";
import { PipelineRunPage } from "./pages/PipelineRunPage";
import { LeadsPage } from "./pages/LeadsPage";
import type { Icp } from "./types";
import "./App.css";

type View =
  | { name: "icps" }
  | { name: "icp-form"; editing: Icp | null }
  | { name: "pipeline-run"; runId: number }
  | { name: "leads"; runId?: number };

function App() {
  const [apiStatus, setApiStatus] = useState<"checking" | "ok" | "error">("checking");
  const [view, setView] = useState<View>({ name: "icps" });

  useEffect(() => {
    api
      .get<{ status: string }>("/api/health")
      .then((res) => setApiStatus(res.status === "ok" ? "ok" : "error"))
      .catch(() => setApiStatus("error"));
  }, []);

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>Prospect Lead</h1>
        <nav className="app-nav">
          <button type="button" className="link-button" onClick={() => setView({ name: "icps" })}>
            ICPs
          </button>
          <button type="button" className="link-button" onClick={() => setView({ name: "leads" })}>
            All Leads
          </button>
        </nav>
        <span className={`api-status api-status-${apiStatus}`}>API: {apiStatus}</span>
      </header>

      <main>
        {view.name === "icps" && (
          <IcpListPage
            onNew={() => setView({ name: "icp-form", editing: null })}
            onEdit={(icp) => setView({ name: "icp-form", editing: icp })}
            onRunStarted={(runId) => setView({ name: "pipeline-run", runId })}
          />
        )}
        {view.name === "icp-form" && (
          <IcpFormPage editing={view.editing} onDone={() => setView({ name: "icps" })} />
        )}
        {view.name === "pipeline-run" && (
          <PipelineRunPage
            runId={view.runId}
            onBack={() => setView({ name: "icps" })}
            onViewLeads={() => setView({ name: "leads", runId: view.runId })}
          />
        )}
        {view.name === "leads" && (
          <LeadsPage
            runId={view.runId}
            onBack={() => setView({ name: "icps" })}
            onRunStarted={(runId) => setView({ name: "pipeline-run", runId })}
          />
        )}
      </main>
    </div>
  );
}

export default App;
