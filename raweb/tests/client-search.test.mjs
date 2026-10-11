import assert from "node:assert/strict";
import test from "node:test";
import { resolveClientSearch } from "../src/client-search.mjs";

test("busca por el único campo ingresado", () => {
  assert.deepEqual(resolveClientSearch({ nombre: " Silvia " }).payload, {
    criterio: "nombre",
    nombre_cliente: "Silvia"
  });
  assert.deepEqual(resolveClientSearch({ direccion: "Italia 50" }).payload, {
    criterio: "direccion",
    direccion: "Italia 50"
  });
  assert.deepEqual(resolveClientSearch({ calle: "Italia", altura: "50" }).payload, {
    criterio: "calle_altura",
    calle: "Italia",
    altura: "50"
  });
  assert.equal(resolveClientSearch({ calle: "Italia" }).payload.altura, null);
});

test("exige un solo criterio", () => {
  assert.equal(resolveClientSearch({}).ok, false);
  assert.equal(resolveClientSearch({ altura: "50" }).ok, false);
  assert.equal(resolveClientSearch({ nombre: "Ana", direccion: "Italia" }).ok, false);
});
