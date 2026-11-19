import assert from "node:assert/strict";
import test from "node:test";
import { interpretAddressQuery } from "../src/address-query.mjs";

test("reconoce latitud,longitud y centra ese par", () => {
  assert.deepEqual(interpretAddressQuery("-35.72,-58.49"), {
    kind: "coordinates",
    lat: -35.72,
    lon: -58.49
  });
  assert.deepEqual(interpretAddressQuery("  -35.720000, -58.490000  "), {
    kind: "coordinates",
    lat: -35.72,
    lon: -58.49
  });
  assert.deepEqual(interpretAddressQuery("-35.72 -58.49"), {
    kind: "coordinates",
    lat: -35.72,
    lon: -58.49
  });
  assert.deepEqual(interpretAddressQuery("(-35.72; -58.49)"), {
    kind: "coordinates",
    lat: -35.72,
    lon: -58.49
  });
  assert.deepEqual(interpretAddressQuery("-35,72,-58,49"), {
    kind: "coordinates",
    lat: -35.72,
    lon: -58.49
  });
  assert.deepEqual(interpretAddressQuery("-90, -180"), {
    kind: "coordinates",
    lat: -90,
    lon: -180
  });
  assert.deepEqual(interpretAddressQuery("90, 180"), {
    kind: "coordinates",
    lat: 90,
    lon: 180
  });
});

test("deja las direcciones para la geocodificación", () => {
  assert.deepEqual(interpretAddressQuery("SARMIENTO 550"), {
    kind: "address",
    direccion: "SARMIENTO 550"
  });
  assert.deepEqual(interpretAddressQuery("  Italia 50  "), {
    kind: "address",
    direccion: "Italia 50"
  });
  assert.equal(interpretAddressQuery("").kind, "empty");
  assert.equal(interpretAddressQuery("   ").kind, "empty");
  assert.equal(interpretAddressQuery("550").kind, "address");
});

test("rechaza pares numéricos fuera de rango", () => {
  assert.equal(interpretAddressQuery("100, 200").kind, "invalid_coordinates");
  assert.equal(interpretAddressQuery("91, 0").kind, "invalid_coordinates");
  assert.equal(interpretAddressQuery("0, 181").kind, "invalid_coordinates");
});
