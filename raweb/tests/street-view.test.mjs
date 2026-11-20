import assert from "node:assert/strict";
import test from "node:test";
import {
  STREET_VIEW_RADIUS_METERS,
  hasStreetViewKey,
  interpretPanoramaStatus,
  streetViewEmbedUrl,
  streetViewExternalUrl
} from "../src/street-view.mjs";

test("la clave vacía no habilita el visor embebido", () => {
  assert.equal(hasStreetViewKey(""), false);
  assert.equal(hasStreetViewKey("   "), false);
  assert.equal(hasStreetViewKey(null), false);
  assert.equal(hasStreetViewKey("__GOOGLE_MAPS_API_KEY__"), false);
  assert.equal(hasStreetViewKey("AIzaExample"), true);
});

test("arma la URL embebida con el panorama y el idioma", () => {
  const url = new URL(streetViewEmbedUrl({ apiKey: "clave demo", panoId: "pano-1" }));
  assert.equal(url.origin + url.pathname, "https://www.google.com/maps/embed/v1/streetview");
  assert.equal(url.searchParams.get("key"), "clave demo");
  assert.equal(url.searchParams.get("pano"), "pano-1");
  assert.equal(url.searchParams.get("language"), "es");
});

test("arma la URL externa con latitud y longitud", () => {
  assert.equal(
    streetViewExternalUrl({ lat: -35.768509, lon: -58.494428 }),
    "https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=-35.768509,-58.494428"
  );
});

test("interpreta la cobertura del panorama", () => {
  const ready = interpretPanoramaStatus("OK", {
    location: {
      pano: "pano-1",
      latLng: { lat: () => -35.77, lng: () => -58.49 }
    }
  });
  assert.deepEqual(ready, {
    state: "ready",
    panorama: { panoId: "pano-1", lat: -35.77, lon: -58.49 }
  });
  assert.deepEqual(interpretPanoramaStatus("ZERO_RESULTS", null), { state: "missing" });
  assert.deepEqual(interpretPanoramaStatus("REQUEST_DENIED", {}), { state: "error" });
  assert.equal(STREET_VIEW_RADIUS_METERS, 50);
});
