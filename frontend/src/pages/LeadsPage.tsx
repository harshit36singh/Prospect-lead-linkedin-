import { useEffect, useMemo, useState } from "react";
import { api } from "../api/client";
import { ExportButtons } from "../components/ExportButtons";
import { StatTile } from "../components/StatTile";
import { GradeBar } from "../components/GradeBar";
import { LeadsTrend } from "../components/LeadsTrend";
import type { Grade, Icp, Lead, PipelineRun } from "../types";

interface LeadsPageProps {
  runId?: number;
  onBack: () => void;
  onRunStarted: (runId: number) => void;
}

const GRADES: Grade[] = ["Hot", "Warm", "Cold"];

export function LeadsPage({ runId, onBack, onRunStarted }: LeadsPageProps) {
  const [icps, setIcps] = useState<Icp[]>([]);
  const [runs, setRuns] = useState<PipelineRun[]>([]);
  const [selectedIcpId, setSelectedIcpId] = useState<number | "">("");
  const [runningPipeline, setRunningPipeline] = useState(false);
  const [runError, setRunError] = useState<string | null>(null);

  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [gradeFilter, setGradeFilter] = useState<Grade | "">("");
  const [minScore, setMinScore] = useState<number | "">("");
  const [showDuplicates, setShowDuplicates] = useState(false);

  useEffect(() => {
    api.get<Icp[]>("/api/icps").then(setIcps).catch(() => undefined);
    api
      .get<PipelineRun[]>("/api/pipeline/runs")
      .then((data) => setRuns(data.slice(0, 10).reverse()))
      .catch(() => undefined);
  }, []);

  useEffect(() => {
    const params = new URLSearchParams();
    if (runId !== undefined) params.set("run_id", String(runId));
    if (gradeFilter) params.set("grade", gradeFilter);
    if (minScore !== "") params.set("min_score", String(minScore));
    if (showDuplicates) params.set("include_duplicates", "true");

    setLoading(true);
    api
      .get<Lead[]>(`/api/leads?${params.toString()}`)
      .then(setLeads)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load leads."))
      .finally(() => setLoading(false));
  }, [runId, gradeFilter, minScore, showDuplicates]);

  const stats = useMemo(() => {
    const companies = new Set(leads.map((l) => l.company.id)).size;
    const contacts = new Set(leads.map((l) => l.contact.id)).size;
    const hot = leads.filter((l) => l.grade === "Hot").length;
    const warm = leads.filter((l) => l.grade === "Warm").length;
    const cold = leads.filter((l) => l.grade === "Cold").length;
    const avgScore = leads.length
      ? Math.round(leads.reduce((sum, l) => sum + l.score, 0) / leads.length)
      : 0;
    return { companies, contacts, hot, warm, cold, avgScore };
  }, [leads]);

  async function handleRunPipeline() {
    if (selectedIcpId === "") return;
    setRunningPipeline(true);
    setRunError(null);
    try {
      const run = await api.post<PipelineRun>("/api/pipeline/runs", { icp_id: selectedIcpId });
      onRunStarted(run.id);
    } catch (err) {
      setRunError(err instanceof Error ? err.message : "Failed to start pipeline run.");
    } finally {
      setRunningPipeline(false);
    }
  }

  const today = new Date().toLocaleDateString(undefined, {
    weekday: "short",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="dashboard">
      <div className="dashboard-header card">
        <div className="dashboard-header-date">
          <span className="dashboard-date">{today}</span>
          <h2>Leads Dashboard</h2>
        </div>
        <div className="dashboard-header-actions">
          <select
            value={selectedIcpId}
            onChange={(e) => setSelectedIcpId(e.target.value === "" ? "" : Number(e.target.value))}
          >
            <option value="">Select an ICP to run...</option>
            {icps.map((icp) => (
              <option key={icp.id} value={icp.id}>
                {icp.name}
              </option>
            ))}
          </select>
          <button type="button" onClick={handleRunPipeline} disabled={selectedIcpId === "" || runningPipeline}>
            {runningPipeline ? "Starting..." : "Run Pipeline"}
          </button>
        </div>
      </div>
      {runError && <p className="form-error">{runError}</p>}

      <div className="stat-tiles-row">
        <StatTile label="Companies discovered" value={stats.companies} />
        <StatTile label="Contacts found" value={stats.contacts} />
        <StatTile label="Hot leads" value={stats.hot} />
        <StatTile label="Avg. score" value={stats.avgScore} />
      </div>

      <div className="dashboard-charts-row">
        <div className="card grade-bar-card">
          <h3>Lead quality</h3>
          <GradeBar hot={stats.hot} warm={stats.warm} cold={stats.cold} />
        </div>
        <div className="card trend-card">
          <h3>Leads per run</h3>
          <LeadsTrend points={runs.map((r) => r.leads_created)} />
        </div>
      </div>

      <div className="card leads-table-card">
        <div className="page-header">
          <div>
            <button type="button" className="link-button" onClick={onBack}>
              &larr; Back to ICPs
            </button>
            <h3>Leads{runId !== undefined ? ` for run #${runId}` : ""}</h3>
          </div>
          <div className="leads-filters">
            <select value={gradeFilter} onChange={(e) => setGradeFilter(e.target.value as Grade | "")}>
              <option value="">All grades</option>
              {GRADES.map((g) => (
                <option key={g} value={g}>
                  {g}
                </option>
              ))}
            </select>
            <input
              type="number"
              placeholder="Min score"
              value={minScore}
              onChange={(e) => setMinScore(e.target.value === "" ? "" : Number(e.target.value))}
            />
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={showDuplicates}
                onChange={(e) => setShowDuplicates(e.target.checked)}
              />
              Show duplicates
            </label>
          </div>
        </div>

        {runId !== undefined && <ExportButtons runId={runId} />}

        {loading && <p>Loading leads...</p>}
        {error && <p className="form-error">{error}</p>}
        {!loading && !error && leads.length === 0 && <p>No leads yet.</p>}

        {!loading && leads.length > 0 && (
          <table className="leads-table">
            <thead>
              <tr>
                <th>Score</th>
                <th>Grade</th>
                <th>Company</th>
                <th>Contact</th>
                <th>Title</th>
                <th>Email</th>
                <th>Email status</th>
                <th>Phone</th>
                {showDuplicates && <th>Duplicate</th>}
              </tr>
            </thead>
            <tbody>
              {leads.map((lead) => (
                <tr key={lead.id} className={lead.is_duplicate ? "duplicate-row" : ""}>
                  <td>{lead.score}</td>
                  <td>
                    <span className={`grade-badge grade-${lead.grade.toLowerCase()}`}>{lead.grade}</span>
                  </td>
                  <td>{lead.company.name}</td>
                  <td>{lead.contact.full_name}</td>
                  <td>{lead.contact.title}</td>
                  <td>{lead.contact.email ?? "—"}</td>
                  <td>{lead.contact.email_verification_status}</td>
                  <td>{lead.contact.phone ?? "—"}</td>
                  {showDuplicates && <td>{lead.is_duplicate ? "Yes" : ""}</td>}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
