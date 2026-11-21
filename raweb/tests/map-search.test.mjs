import assert from "node:assert/strict";
import test from "node:test";
import { mapSearchPath, SEARCH_DEBOUNCE_MS } from "../src/map-search.mjs";

test("no consulta con menos de 3 caracteres", () => {
  assert.equal(mapSearchPath(""), null);
  assert.equal(mapSearchPath("  a "), null);
  assert.equal(mapSearchPath("ca"), null);
  assert.equal(mapSearchPath("  ca  "), null);
});

test("arma la ruta desde el tercer caracter", () => {
  assert.equal(mapSearchPath("cas"), "/mapa/buscar?q=cas");
  assert.equal(mapSearchPath("  cas  "), "/mapa/buscar?q=cas");
  assert.equal(mapSearchPath("López 12"), "/mapa/buscar?q=L%C3%B3pez%2012");
  assert.equal(SEARCH_DEBOUNCE_MS, 300);
});
