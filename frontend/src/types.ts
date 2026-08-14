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

export interface Company {
  id: number;
  name: string;
  domain: string;
  industry: string;
  size_label: string;
  size_min: number | null;
  size_max: number | null;
  location: string;
  technologies: string[];
  github_org: string | null;
  source: string;
  created_at: string;
}

export interface Contact {
  id: number;
  company_id: number;
  full_name: string;
  title: string;
  location: string;
  email: string | null;
  email_confidence: number;
  email_source: string | null;
  email_verification_status: string;
  phone: string | null;
  phone_confidence: number;
  phone_verification_status: string;
  is_duplicate: boolean;
  duplicate_of_contact_id: number | null;
  created_at: string;
}

export type Grade = "Hot" | "Warm" | "Cold";

export interface Lead {
  id: number;
  pipeline_run_id: number;
  icp_id: number;
  score: number;
  grade: Grade;
  score_breakdown: Record<string, number | string>;
  is_duplicate: boolean;
  exported_to_sheets_at: string | null;
  exported_pdf_path: string | null;
  created_at: string;
  company: Company;
  contact: Contact;
}
