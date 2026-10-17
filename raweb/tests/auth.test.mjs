import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import { fetchConBearer } from "../src/auth/api-client.mjs";
import { crearConfigOidc } from "../src/auth/oidc-config.mjs";

test("la configuración OIDC usa el realm rancho y el cliente raweb con PKCE", () => {
  const config = crearConfigOidc({
    url: "http://localhost:8081/",
    realm: "rancho",
    clientId: "raweb"
  });
  assert.equal(config.realm, "rancho");
  assert.equal(config.clientId, "raweb");
  assert.equal(config.pkceMethod, "S256");
  assert.equal(config.clientSecret, undefined);
  assert.equal(config.url, "http://localhost:8081");
});

test("rechaza otro realm o un client secret implícito en el nombre", () => {
  assert.throws(() => crearConfigOidc({ url: "http://localhost:8081", realm: "fibergis", clientId: "raweb" }));
  assert.throws(() => crearConfigOidc({ url: "http://localhost:8081", realm: "rancho", clientId: "ra-web" }));
});

test("agrega Bearer y ante 401 refresca una vez", async () => {
  const llamadas = [];
  const response = await fetchConBearer({
    fetchImpl: async (url, options) => {
      llamadas.push(options.headers.get("Authorization"));
      return { status: llamadas.length === 1 ? 401 : 200 };
    },
    getToken: async () => "token-viejo",
    refresh: async () => "token-nuevo",
    logout: async () => {
      throw new Error("no debería cerrar sesión");
    },
    url: "http://localhost:5000/api/clientes/buscar"
  });
  assert.equal(response.status, 200);
  assert.deepEqual(llamadas, ["Bearer token-viejo", "Bearer token-nuevo"]);
});

test("cierra sesión si el refresh sigue en 401 y conserva el 403", async () => {
  let cerro = false;
  const noAutorizado = await fetchConBearer({
    fetchImpl: async () => ({ status: 401 }),
    getToken: async () => "a",
    refresh: async () => "b",
    logout: async () => {
      cerro = true;
    },
    url: "http://localhost:5000/api/clientes/buscar"
  });
  assert.equal(noAutorizado.status, 401);
  assert.equal(cerro, true);

  cerro = false;
  const prohibido = await fetchConBearer({
    fetchImpl: async () => ({ status: 403 }),
    getToken: async () => "a",
    refresh: async () => {
      throw new Error("403 no refresca");
    },
    logout: async () => {
      cerro = true;
    },
    url: "http://localhost:5000/api/clientes/actualizar/1"
  });
  assert.equal(prohibido.status, 403);
  assert.equal(cerro, false);
});

test("la landing no pide credenciales y ofrece Keycloak", () => {
  const app = readFileSync(new URL("../src/App.svelte", import.meta.url), "utf8");
  const cuenta = readFileSync(new URL("../src/AccountMenu.svelte", import.meta.url), "utf8");
  const sesion = readFileSync(new URL("../src/auth/session.mjs", import.meta.url), "utf8");
  const botonClave = cuenta.slice(Math.max(0, cuenta.indexOf("Cambiar contraseña") - 250), cuenta.indexOf("Cambiar contraseña"));
  assert.match(app, /Ingresar con Keycloak/);
  assert.match(cuenta, /Cerrar sesión/);
  assert.match(cuenta, /Cambiar contraseña/);
  assert.equal(botonClave.includes("disabled"), false);
  assert.match(sesion, /action:\s*"UPDATE_PASSWORD"/);
  assert.equal(app.includes('type="password"'), false);
  assert.equal(cuenta.includes('type="password"'), false);
  assert.equal(cuenta.includes("UPDATE_PASSWORD"), false);
  assert.equal(app.includes("ra-web"), false);
});
