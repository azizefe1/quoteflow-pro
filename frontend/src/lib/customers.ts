import { apiRequest } from "@/lib/api";

export type CustomerResponse = {
  id: string;
  company_id: string;
  name: string;
  contact_name: string | null;
  email: string | null;
  phone: string | null;
  tax_number: string | null;
  address: string | null;
  notes: string | null;
  is_active: boolean;
};

export type CustomerListResponse = {
  total: number;
  limit: number;
  offset: number;
  items: CustomerResponse[];
};

export type CustomerCreatePayload = {
  name: string;
  contact_name?: string;
  email?: string;
  phone?: string;
  tax_number?: string;
  address?: string;
  notes?: string;
};

export function listCustomers(
  token: string,
  companyId: string,
  params: {
    search?: string;
    limit?: number;
    offset?: number;
    includeInactive?: boolean;
  } = {},
): Promise<CustomerListResponse> {
  const searchParams = new URLSearchParams();

  if (params.search) {
    searchParams.set("search", params.search);
  }

  searchParams.set("limit", String(params.limit ?? 20));
  searchParams.set("offset", String(params.offset ?? 0));

  if (params.includeInactive) {
    searchParams.set("include_inactive", "true");
  }

  return apiRequest<CustomerListResponse>(
    `/api/companies/${companyId}/customers?${searchParams.toString()}`,
    {
      token,
    },
  );
}

export function createCustomer(
  token: string,
  companyId: string,
  payload: CustomerCreatePayload,
): Promise<CustomerResponse> {
  return apiRequest<CustomerResponse>(`/api/companies/${companyId}/customers`, {
    method: "POST",
    token,
    body: payload,
  });
}

export function deactivateCustomer(
  token: string,
  companyId: string,
  customerId: string,
): Promise<CustomerResponse> {
  return apiRequest<CustomerResponse>(
    `/api/companies/${companyId}/customers/${customerId}`,
    {
      method: "DELETE",
      token,
    },
  );
}
