export async function fetchConBearer({ fetchImpl, getToken, refresh, logout, url, options = {} }) {
  const headers = new Headers(options.headers || {});
  headers.set("Authorization", `Bearer ${await getToken()}`);
  let response = await fetchImpl(url, { ...options, headers });
  if (response.status === 401) {
    headers.set("Authorization", `Bearer ${await refresh()}`);
    response = await fetchImpl(url, { ...options, headers });
    if (response.status === 401) {
      await logout();
    }
  }
  return response;
}
