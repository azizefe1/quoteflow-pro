export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

type ApiBody = Record<string, unknown> | Array<unknown> | string | undefined;

type ApiRequestOptions = Omit<RequestInit, "body"> & {
  token?: string;
  body?: ApiBody;
};

type ApiErrorResponse = {
  detail?: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type UserResponse = {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
};

export async function apiRequest<T>(
  path: string,
  options: ApiRequestOptions = {},
): Promise<T> {
  const { token, body, headers, ...requestOptions } = options;

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...requestOptions,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  const contentType = response.headers.get("content-type");
  const responseBody = contentType?.includes("application/json")
    ? ((await response.json()) as ApiErrorResponse | T)
    : await response.text();

  if (!response.ok) {
    const detail =
      typeof responseBody === "object" && responseBody !== null && "detail" in responseBody
        ? responseBody.detail
        : undefined;

    throw new Error(detail ?? `API request failed with status ${response.status}`);
  }

  return responseBody as T;
}
