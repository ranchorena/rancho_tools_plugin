import assert from "node:assert/strict";
import test from "node:test";
import {
  buildRoutePayload,
  formatCoordinates,
  formatDistance,
  isValidPoint,
  swapPoints
} from "../src/route-planner.mjs";

test("valida puntos con coordenadas en rango", () => {
  assert.equal(isValidPoint({ lat: -34.6, lon: -58.4 }), true);
  assert.equal(isValidPoint({ lat: "-34.6", lon: -58.4 }), false);
  assert.equal(isValidPoint({ lat: 95, lon: -58.4 }), false);
  assert.equal(isValidPoint({ lat: -34.6, lon: NaN }), false);
  assert.equal(isValidPoint(null), false);
});

test("arma el payload solo con origen y destino válidos", () => {
  assert.deepEqual(
    buildRoutePayload({ lat: -34.6, lon: -58.4 }, { lat: -34.7, lon: -58.5 }),
    {
      ok: true,
      payload: {
        origen: { latitud: -34.6, longitud: -58.4 },
        destino: { latitud: -34.7, longitud: -58.5 }
      }
    }
  );
  assert.equal(buildRoutePayload(null, { lat: -34.7, lon: -58.5 }).ok, false);
  assert.equal(buildRoutePayload({ lat: -34.6, lon: -58.4 }, undefined).ok, false);
});

test("formatea la distancia en metros o kilómetros", () => {
  assert.equal(formatDistance(850), "850 m");
  assert.equal(formatDistance(999.6), "1,0 km");
  assert.equal(formatDistance(1234), "1,2 km");
  assert.equal(formatDistance(-1), "");
});

test("intercambia origen y destino", () => {
  const a = { lat: 1, lon: 2 };
  const b = { lat: 3, lon: 4 };
  assert.deepEqual(swapPoints(a, b), { origin: b, destination: a });
});

test("muestra coordenadas como latitud, longitud", () => {
  assert.equal(formatCoordinates({ lat: -34.5959975, lon: -58.3893392 }), "-34.595998, -58.389339");
});
