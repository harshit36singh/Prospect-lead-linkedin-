import { useEffect, useState } from "react";
import { api } from "./api/client";
import "./App.css";

function App() {
  const [apiStatus, setApiStatus] = useState<"checking" | "ok" | "error">("checking");

  useEffect(() => {
    api
      .get<{ status: string }>("/api/health")
      .then((res) => setApiStatus(res.status === "ok" ? "ok" : "error"))
      .catch(() => setApiStatus("error"));
  }, []);

  return (
    <div className="app-shell">
      <h1>Prospect Lead</h1>
      <p>Backend status: {apiStatus}</p>
    </div>
  );
}

export default App;
