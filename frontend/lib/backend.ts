export type BackendProject = {
  id: string;
  name: string;
  project_name?: string;
  project_type?: string;
  client: string;
  status: 'active' | 'archived';
  hours: number;
  cost: number;
  team_size: number;
  generated_at: string;
  input_project?: string;
  estimation?: string;
  llm_analysis?: string;
};

export function getBackendUrl() {
  return process.env.NEXT_PUBLIC_BACKEND_URL?.replace(/\/$/, '') ?? '';
}
