import { useState } from "react";
import { api, ApiError } from "../api/client";

interface ExportButtonsProps {
  runId: number;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export function ExportButtons({ runId }: ExportButtonsProps) {
  const [pdfWorking, setPdfWorking] = useState(false);
  const [pdfError, setPdfError] = useState<string | null>(null);

  const [sheetName, setSheetName] = useState("Prospect Leads");
  const [sheetsWorking, setSheetsWorking] = useState(false);
  const [sheetsError, setSheetsError] = useState<string | null>(null);
  const [sheetUrl, setSheetUrl] = useState<string | null>(null);

  async function handlePdf() {
    setPdfWorking(true);
    setPdfError(null);
    try {
      const res = await api.post<{ filename: string; lead_count: number }>("/api/exports/pdf", {
        run_id: runId,
      });
      window.open(`${API_BASE_URL}/api/exports/pdf/${res.filename}`, "_blank");
    } catch (err) {
      setPdfError(err instanceof ApiError ? err.message : "PDF export failed.");
    } finally {
      setPdfWorking(false);
    }
  }

  async function handleSheets() {
    setSheetsWorking(true);
    setSheetsError(null);
    setSheetUrl(null);
    try {
      const res = await api.post<{ sheet_url: string; lead_count: number }>("/api/exports/sheets", {
        run_id: runId,
        sheet_name: sheetName,
      });
      setSheetUrl(res.sheet_url);
    } catch (err) {
      setSheetsError(err instanceof ApiError ? err.message : "Sheets export failed.");
    } finally {
      setSheetsWorking(false);
    }
  }

  return (
    <div className="export-buttons">
      <div className="export-action">
        <button type="button" onClick={handlePdf} disabled={pdfWorking}>
          {pdfWorking ? "Generating..." : "Download PDF"}
        </button>
        {pdfError && <p className="form-error">{pdfError}</p>}
      </div>

      <div className="export-action">
        <input
          type="text"
          value={sheetName}
          onChange={(e) => setSheetName(e.target.value)}
          placeholder="Sheet name"
        />
        <button type="button" onClick={handleSheets} disabled={sheetsWorking}>
          {sheetsWorking ? "Exporting..." : "Export to Sheets"}
        </button>
        {sheetsError && <p className="form-error">{sheetsError}</p>}
        {sheetUrl && (
          <p className="export-success">
            <a href={sheetUrl} target="_blank" rel="noreferrer">
              Open sheet &rarr;
            </a>
          </p>
        )}
      </div>
    </div>
  );
}
