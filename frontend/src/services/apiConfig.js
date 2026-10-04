// Centralized API Base URL configuration
// If VITE_API_URL is set (e.g. in Vercel or local .env), use it; otherwise fallback to the live Render deployment.
export const API_URL = (
  import.meta.env.VITE_API_URL || "https://cognitiveops.onrender.com"
).replace(/\/+$/, "");

export default API_URL;
