export const env = {
  API_BASE_URL: process.env.VITE_API_BASE_URL || "http://localhost:8000",
  SUPABASE_URL: process.env.VITE_SUPABASE_URL || "",
  SUPABASE_ANON_KEY: process.env.VITE_SUPABASE_ANON_KEY || "",
};

// Validate that required env variables are present and fail fast
if (!env.SUPABASE_URL) {
  throw new Error("Missing environment variable: VITE_SUPABASE_URL");
}
if (!env.SUPABASE_ANON_KEY) {
  throw new Error("Missing environment variable: VITE_SUPABASE_ANON_KEY");
}
