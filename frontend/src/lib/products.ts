import { apiRequest } from "@/lib/api";

export type ProductResponse = {
  id: string;
  company_id: string;
  sku: string | null;
  name: string;
  description: string | null;
  unit: string;
  unit_price: string;
  currency: string;
  tax_rate: string;
  stock_quantity: string;
  is_active: boolean;
};

export type ProductListResponse = {
  total: number;
  limit: number;
  offset: number;
  items: ProductResponse[];
};

export type ProductCreatePayload = {
  sku?: string;
  name: string;
  description?: string;
  unit: string;
  unit_price: string;
  currency: string;
  tax_rate: string;
  stock_quantity: string;
};

export type ProductUpdatePayload = Partial<ProductCreatePayload>;

export function listProducts(
  token: string,
  companyId: string,
  params: {
    search?: string;
    limit?: number;
    offset?: number;
    includeInactive?: boolean;
  } = {},
): Promise<ProductListResponse> {
  const searchParams = new URLSearchParams();

  if (params.search) {
    searchParams.set("search", params.search);
  }

  searchParams.set("limit", String(params.limit ?? 20));
  searchParams.set("offset", String(params.offset ?? 0));

  if (params.includeInactive) {
    searchParams.set("include_inactive", "true");
  }

  return apiRequest<ProductListResponse>(
    `/api/companies/${companyId}/products?${searchParams.toString()}`,
    { token },
  );
}

export function getProduct(
  token: string,
  companyId: string,
  productId: string,
): Promise<ProductResponse> {
  return apiRequest<ProductResponse>(
    `/api/companies/${companyId}/products/${productId}`,
    { token },
  );
}

export function createProduct(
  token: string,
  companyId: string,
  payload: ProductCreatePayload,
): Promise<ProductResponse> {
  return apiRequest<ProductResponse>(`/api/companies/${companyId}/products`, {
    method: "POST",
    token,
    body: payload,
  });
}

export function updateProduct(
  token: string,
  companyId: string,
  productId: string,
  payload: ProductUpdatePayload,
): Promise<ProductResponse> {
  return apiRequest<ProductResponse>(
    `/api/companies/${companyId}/products/${productId}`,
    {
      method: "PATCH",
      token,
      body: payload,
    },
  );
}

export function deactivateProduct(
  token: string,
  companyId: string,
  productId: string,
): Promise<ProductResponse> {
  return apiRequest<ProductResponse>(
    `/api/companies/${companyId}/products/${productId}`,
    {
      method: "DELETE",
      token,
    },
  );
}
