export interface Icp {
  id: number;
  name: string;
  industries: string[];
  company_size_min: number | null;
  company_size_max: number | null;
  locations: string[];
  technologies: string[];
  target_titles: string[];
  created_at: string;
  updated_at: string;
}

export type IcpInput = Omit<Icp, "id" | "created_at" | "updated_at">;

export type PipelineRunStatus = "pending" | "running" | "completed" | "failed";

export interface PipelineRun {
  id: number;
  icp_id: number;
  status: PipelineRunStatus;
  stage: string;
  started_at: string | null;
  finished_at: string | null;
  companies_found: number;
  contacts_found: number;
  leads_created: number;
  error_message: string | null;
  created_at: string;
}
