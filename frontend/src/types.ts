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
