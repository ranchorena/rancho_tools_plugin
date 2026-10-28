export function isValidPoint(point) {
  if (!point) return false;
  const { lat, lon } = point;
  return typeof lat === "number" && typeof lon === "number"
    && Number.isFinite(lat) && Number.isFinite(lon)
    && lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180;
}

export function buildRoutePayload(origin, destination) {
  if (!isValidPoint(origin)) return { ok: false, message: "Indicá el origen." };
  if (!isValidPoint(destination)) return { ok: false, message: "Indicá el destino." };
  return {
    ok: true,
    payload: {
      origen: { latitud: origin.lat, longitud: origin.lon },
      destino: { latitud: destination.lat, longitud: destination.lon }
    }
  };
}

export function formatDistance(meters) {
  if (typeof meters !== "number" || !Number.isFinite(meters) || meters < 0) return "";
  const rounded = Math.round(meters);
  if (rounded < 1000) return `${rounded} m`;
  return `${(meters / 1000).toFixed(1).replace(".", ",")} km`;
}

export function swapPoints(origin, destination) {
  return { origin: destination, destination: origin };
}

export function formatCoordinates({ lat, lon }) {
  return `${lat.toFixed(6)}, ${lon.toFixed(6)}`;
}
