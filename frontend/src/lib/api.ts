import { supabase } from "./supabase";
import { env } from "./env";

export async function getAuthHeaders(): Promise<HeadersInit> {
  const { data: { session } } = await supabase.auth.getSession();
  const token = session?.access_token;
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${env.API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...headers,
      ...options.headers,
    },
  });

  if (!response.ok) {
    let errorDetail = "";
    try {
      const errJson = await response.json();
      errorDetail = errJson?.detail || "";
    } catch {
      // Fallback if response is not JSON
    }
    throw new Error(errorDetail || `HTTP error! Status: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function apiFetchStream(path: string, options: RequestInit = {}): Promise<Response> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${env.API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...headers,
      ...options.headers,
    },
  });

  if (!response.ok) {
    let errorDetail = "";
    try {
      const errJson = await response.json();
      errorDetail = errJson?.detail || "";
    } catch {
      // Fallback
    }
    throw new Error(errorDetail || `HTTP error! Status: ${response.status}`);
  }

  return response;
}
