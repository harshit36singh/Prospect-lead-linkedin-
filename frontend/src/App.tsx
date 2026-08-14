import { useEffect, useState } from "react";
import { api } from "./api/client";
import { IcpListPage } from "./pages/IcpListPage";
import { IcpFormPage } from "./pages/IcpFormPage";
import type { Icp } from "./types";
import "./App.css";

type View = { name: "icps" } | { name: "icp-form"; editing: Icp | null };

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
        <span className={`api-status api-status-${apiStatus}`}>API: {apiStatus}</span>
      </header>

      <main>
        {view.name === "icps" && (
          <IcpListPage
            onNew={() => setView({ name: "icp-form", editing: null })}
            onEdit={(icp) => setView({ name: "icp-form", editing: icp })}
          />
        )}
        {view.name === "icp-form" && (
          <IcpFormPage editing={view.editing} onDone={() => setView({ name: "icps" })} />
        )}
      </main>
    </div>
  );
}

export default App;
