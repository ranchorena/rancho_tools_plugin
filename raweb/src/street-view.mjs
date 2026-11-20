// Radio con el que Google busca la foto más cercana al punto elegido.
// La consulta de cobertura no se cobra. El visor es el iframe de Maps Embed API.
export const STREET_VIEW_RADIUS_METERS = 50;

const unconfiguredKey = "__" + "GOOGLE_MAPS_API_KEY" + "__";

export function hasStreetViewKey(apiKey) {
  return typeof apiKey === "string"
    && apiKey.trim().length > 0
    && apiKey !== unconfiguredKey;
}

export function streetViewEmbedUrl({ apiKey, panoId }) {
  const params = new URLSearchParams({
    key: apiKey,
    pano: panoId,
    language: "es"
  });
  return `https://www.google.com/maps/embed/v1/streetview?${params.toString()}`;
}

export function streetViewExternalUrl({ lat, lon }) {
  return `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${lat},${lon}`;
}

export function interpretPanoramaStatus(status, data) {
  const panoId = data?.location?.pano;
  if (status === "OK" && typeof panoId === "string" && panoId.length > 0) {
    const position = data.location.latLng;
    return {
      state: "ready",
      panorama: {
        panoId,
        lat: typeof position?.lat === "function" ? position.lat() : null,
        lon: typeof position?.lng === "function" ? position.lng() : null
      }
    };
  }
  if (status === "ZERO_RESULTS") return { state: "missing" };
  return { state: "error" };
}
