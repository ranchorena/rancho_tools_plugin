import Keycloak from "keycloak-js";

import { KEYCLOAK_CLIENT_ID, KEYCLOAK_REALM, KEYCLOAK_URL } from "../config.js";
import { fetchConBearer } from "./api-client.mjs";
import { crearConfigOidc } from "./oidc-config.mjs";

let keycloak;

function sesion() {
  const claims = keycloak?.tokenParsed || {};
  return {
    authenticated: Boolean(keycloak?.authenticated),
    username: claims.preferred_username || claims.email || ""
  };
}

export async function initAuth() {
  const config = crearConfigOidc({
    url: KEYCLOAK_URL,
    realm: KEYCLOAK_REALM,
    clientId: KEYCLOAK_CLIENT_ID
  });
  keycloak = new Keycloak({
    url: config.url,
    realm: config.realm,
    clientId: config.clientId
  });
  await keycloak.init({
    pkceMethod: config.pkceMethod,
    onLoad: "check-sso",
    silentCheckSsoRedirectUri: `${window.location.origin}/silent-check-sso.html`,
    checkLoginIframe: false
  });
  return sesion();
}

export function login() {
  return keycloak.login({ redirectUri: `${window.location.origin}/` });
}

export function cambiarContrasena() {
  return keycloak.login({
    action: "UPDATE_PASSWORD",
    redirectUri: `${window.location.origin}/`
  });
}

export function logout() {
  return keycloak.logout({ redirectUri: `${window.location.origin}/` });
}

export function authorizedFetch(url, options = {}) {
  return fetchConBearer({
    fetchImpl: fetch,
    getToken: async () => {
      await keycloak.updateToken(30);
      return keycloak.token;
    },
    refresh: async () => {
      await keycloak.updateToken(-1);
      return keycloak.token;
    },
    logout,
    url,
    options
  });
}
