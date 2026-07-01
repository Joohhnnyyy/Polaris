export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
export const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000";

export const safeFetchArray = <T = any>(url: string): Promise<T[]> =>
  fetch(url)
    .then((r) => (r.ok ? r.json() : []))
    .then((data) => (Array.isArray(data) ? data : []))
    .catch(() => []);

export const resolveImageUrl = (url: string): string => {
  if (!url) return "";
  // Rewrite Cloud Run ephemeral static URLs to their persistent Supabase storage equivalents
  if (url.includes("/static/") && !url.includes("localhost") && !url.includes("127.0.0.1")) {
    const filename = url.split("/static/").pop()?.split("?")[0];
    if (filename) {
      return `https://eujwgicfoyrjxwnvdjzv.supabase.co/storage/v1/object/public/civicmind-images/public/${filename}`;
    }
  }
  return url;
};
