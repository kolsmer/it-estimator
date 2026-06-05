import { getBackendUrl } from '@/lib/backend';
import { BackendProject } from '@/lib/backend';

export type RoleRate = {
  id: string;
  role: string;
  rate: number;
  currency: string;
  role_key: string;
  seniority: string;
};

function getServerBackendUrl() {
  return process.env.BACKEND_URL_INTERNAL?.replace(/\/$/, '') || getBackendUrl();
}

async function readJson<T>(url: string): Promise<T | null> {
  try {
    const response = await fetch(url, { cache: 'no-store' });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export async function fetchProjects() {
  const backendUrl = getServerBackendUrl();
  if (!backendUrl) return [];
  return (await readJson<BackendProject[]>(`${backendUrl}/projects`)) ?? [];
}

export async function fetchArchivedProjects() {
  const backendUrl = getServerBackendUrl();
  if (!backendUrl) return [];
  return (await readJson<BackendProject[]>(`${backendUrl}/projects/archived`)) ?? [];
}

export async function fetchRoleRates() {
  const backendUrl = getServerBackendUrl();
  if (!backendUrl) return [];
  return (await readJson<RoleRate[]>(`${backendUrl}/roles`)) ?? [];
}
