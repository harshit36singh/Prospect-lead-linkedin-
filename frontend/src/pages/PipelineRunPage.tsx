import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { PipelineRun } from "../types";

interface PipelineRunPageProps {
  runId: number;
  onViewLeads: () => void;
  onBack: () => void;
}

const POLL_INTERVAL_MS = 1500;

export function PipelineRunPage({ runId, onViewLeads, onBack }: PipelineRunPageProps) {
  const [run, setRun] = useState<PipelineRun | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout>;

    async function poll() {
      try {
        const data = await api.get<PipelineRun>(`/api/pipeline/runs/${runId}`);
        if (cancelled) return;
        setRun(data);
        if (data.status === "pending" || data.status === "running") {
          timer = setTimeout(poll, POLL_INTERVAL_MS);
        }
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load run status.");
      }
    }

    poll();
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [runId]);

  if (error) return <p className="form-error">{error}</p>;
  if (!run) return <p>Loading run status...</p>;

  const isActive = run.status === "pending" || run.status === "running";

  return (
    <div className="pipeline-run-page">
      <button type="button" className="link-button" onClick={onBack}>
        &larr; Back to ICPs
      </button>
      <h2>Pipeline run #{run.id}</h2>
      <p>
        Status: <strong>{run.status}</strong>
        {isActive && <> &mdash; stage: {run.stage || "starting"}</>}
      </p>
      <div className="run-stats">
        <div>
          <span className="stat-value">{run.companies_found}</span>
          <span className="stat-label">Companies found</span>
        </div>
        <div>
          <span className="stat-value">{run.contacts_found}</span>
          <span className="stat-label">Contacts found</span>
        </div>
        <div>
          <span className="stat-value">{run.leads_created}</span>
          <span className="stat-label">Leads created</span>
        </div>
      </div>
      {run.status === "failed" && <p className="form-error">Run failed: {run.error_message}</p>}
      {run.status === "completed" && (
        <button type="button" onClick={onViewLeads}>
          View leads
        </button>
      )}
    </div>
  );
}
