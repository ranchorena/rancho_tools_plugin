export const SEARCH_DEBOUNCE_MS = 300;

export function mapSearchPath(text) {
  const q = String(text ?? "").trim();
  if (q.length < 3) return null;
  return `/mapa/buscar?q=${encodeURIComponent(q)}`;
}
