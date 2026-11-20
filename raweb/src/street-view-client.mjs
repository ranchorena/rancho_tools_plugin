import { STREET_VIEW_RADIUS_METERS, interpretPanoramaStatus } from "./street-view.mjs";

let loading = null;

export function loadGoogleMaps(apiKey) {
  if (typeof window !== "undefined" && window.google?.maps?.StreetViewService) {
    return Promise.resolve(window.google.maps);
  }
  if (loading) return loading;
  loading = new Promise((resolve, reject) => {
    const callbackName = "raStreetViewInit";
    const fail = (error) => {
      delete window[callbackName];
      loading = null;
      reject(error);
    };
    window[callbackName] = () => {
      delete window[callbackName];
      const maps = window.google?.maps;
      if (!maps?.StreetViewService) {
        loading = null;
        reject(new Error("Street View no está disponible"));
        return;
      }
      resolve(maps);
    };
    const script = document.createElement("script");
    script.async = true;
    script.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(apiKey)}&v=weekly&loading=async&callback=${callbackName}`;
    script.onerror = () => fail(new Error("No se pudo cargar Street View"));
    document.head.appendChild(script);
  });
  return loading;
}

export function queryNearestPanorama(maps, point, radiusMeters = STREET_VIEW_RADIUS_METERS) {
  const service = new maps.StreetViewService();
  const request = {
    location: { lat: point.lat, lng: point.lon },
    radius: radiusMeters
  };
  if (maps.StreetViewSource?.OUTDOOR) {
    request.source = maps.StreetViewSource.OUTDOOR;
  }
  return new Promise((resolve) => {
    service.getPanorama(request, (data, status) => {
      resolve(interpretPanoramaStatus(status, data));
    });
  });
}
