export function crearConfigOidc({ url, realm, clientId }) {
  if (realm !== "rancho") {
    throw new Error("El realm OIDC debe ser rancho.");
  }
  if (clientId !== "raweb") {
    throw new Error("El client id de la web debe ser raweb.");
  }
  if (!url || url.includes("fibergis")) {
    throw new Error("La URL de Keycloak no es válida.");
  }
  return {
    url: url.replace(/\/$/, ""),
    realm,
    clientId,
    pkceMethod: "S256",
    clientSecret: undefined
  };
}
