import { apiRequest } from "@/lib/api";

export type CompanyResponse = {
  id: string;
  name: string;
  slug: string;
  industry: string | null;
  email: string | null;
  phone: string | null;
  website: string | null;
  tax_number: string | null;
  address: string | null;
};

export type CompanyWorkspaceResponse = {
  membership_id: string;
  role: string;
  company: CompanyResponse;
};

export type CompanyCreatePayload = {
  name: string;
  industry?: string;
  email?: string;
  phone?: string;
  website?: string;
  tax_number?: string;
  address?: string;
};

export function listMyCompanyWorkspaces(
  token: string,
): Promise<CompanyWorkspaceResponse[]> {
  return apiRequest<CompanyWorkspaceResponse[]>("/api/companies/me", {
    token,
  });
}

export function getCompanyWorkspace(
  token: string,
  companyId: string,
): Promise<CompanyWorkspaceResponse> {
  return apiRequest<CompanyWorkspaceResponse>(`/api/companies/${companyId}`, {
    token,
  });
}

export function createCompanyWorkspace(
  token: string,
  payload: CompanyCreatePayload,
): Promise<CompanyWorkspaceResponse> {
  return apiRequest<CompanyWorkspaceResponse>("/api/companies", {
    method: "POST",
    token,
    body: payload,
  });
}
