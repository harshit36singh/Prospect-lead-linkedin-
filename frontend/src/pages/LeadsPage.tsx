import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { Grade, Lead } from "../types";

interface LeadsPageProps {
  runId?: number;
  onBack: () => void;
}

const GRADES: Grade[] = ["Hot", "Warm", "Cold"];

export function LeadsPage({ runId, onBack }: LeadsPageProps) {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [gradeFilter, setGradeFilter] = useState<Grade | "">("");
  const [minScore, setMinScore] = useState<number | "">("");

  useEffect(() => {
    const params = new URLSearchParams();
    if (runId !== undefined) params.set("run_id", String(runId));
    if (gradeFilter) params.set("grade", gradeFilter);
    if (minScore !== "") params.set("min_score", String(minScore));

    setLoading(true);
    api
      .get<Lead[]>(`/api/leads?${params.toString()}`)
      .then(setLeads)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load leads."))
      .finally(() => setLoading(false));
  }, [runId, gradeFilter, minScore]);

  return (
    <div className="leads-page">
      <button type="button" className="link-button" onClick={onBack}>
        &larr; Back to ICPs
      </button>
      <div className="page-header">
        <h2>Leads{runId !== undefined ? ` for run #${runId}` : ""}</h2>
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
        </div>
      </div>

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
            </tr>
          </thead>
          <tbody>
            {leads.map((lead) => (
              <tr key={lead.id}>
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
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
