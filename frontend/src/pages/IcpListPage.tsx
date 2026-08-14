import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { Icp, PipelineRun } from "../types";

interface IcpListPageProps {
  onNew: () => void;
  onEdit: (icp: Icp) => void;
  onRunStarted: (runId: number) => void;
}

export function IcpListPage({ onNew, onEdit, onRunStarted }: IcpListPageProps) {
  const [icps, setIcps] = useState<Icp[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [runningIcpId, setRunningIcpId] = useState<number | null>(null);

  function load() {
    setLoading(true);
    api
      .get<Icp[]>("/api/icps")
      .then(setIcps)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load ICPs."))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    load();
  }, []);

  async function handleDelete(id: number) {
    if (!confirm("Delete this ICP?")) return;
    await api.delete(`/api/icps/${id}`);
    load();
  }

  async function handleRun(icpId: number) {
    setRunningIcpId(icpId);
    try {
      const run = await api.post<PipelineRun>("/api/pipeline/runs", { icp_id: icpId });
      onRunStarted(run.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start pipeline run.");
    } finally {
      setRunningIcpId(null);
    }
  }

  if (loading) return <p>Loading ICPs...</p>;
  if (error) return <p className="form-error">{error}</p>;

  return (
    <div className="icp-list-page">
      <div className="page-header">
        <h2>Ideal Customer Profiles</h2>
        <button type="button" onClick={onNew}>
          New ICP
        </button>
      </div>

      {icps.length === 0 ? (
        <p>No ICPs yet. Create one to start discovering leads.</p>
      ) : (
        <table className="icp-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Industries</th>
              <th>Size</th>
              <th>Locations</th>
              <th>Technologies</th>
              <th>Target titles</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {icps.map((icp) => (
              <tr key={icp.id}>
                <td>{icp.name}</td>
                <td>{icp.industries.join(", ")}</td>
                <td>
                  {icp.company_size_min ?? "?"}-{icp.company_size_max ?? "?"}
                </td>
                <td>{icp.locations.join(", ")}</td>
                <td>{icp.technologies.join(", ")}</td>
                <td>{icp.target_titles.join(", ")}</td>
                <td className="row-actions">
                  <button
                    type="button"
                    onClick={() => handleRun(icp.id)}
                    disabled={runningIcpId === icp.id}
                  >
                    {runningIcpId === icp.id ? "Starting..." : "Run Pipeline"}
                  </button>
                  <button type="button" onClick={() => onEdit(icp)}>
                    Edit
                  </button>
                  <button type="button" onClick={() => handleDelete(icp.id)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
