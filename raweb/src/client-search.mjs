export function resolveClientSearch({ nombre = "", direccion = "", calle = "", altura = "" } = {}) {
  const name = String(nombre).trim();
  const address = String(direccion).trim();
  const street = String(calle).trim();
  const height = String(altura).trim();
  const groups = [];

  if (name) groups.push("nombre");
  if (address) groups.push("direccion");
  if (street || height) groups.push("calle_altura");

  if (groups.length === 0) {
    return {
      ok: false,
      message: "Ingrese un nombre, una dirección o una calle."
    };
  }

  if (groups.length > 1) {
    return {
      ok: false,
      message: "Complete un solo criterio de búsqueda."
    };
  }

  if (groups[0] === "calle_altura" && !street) {
    return {
      ok: false,
      message: "Ingrese el nombre de la calle."
    };
  }

  if (groups[0] === "nombre") {
    return {
      ok: true,
      payload: { criterio: "nombre", nombre_cliente: name },
      emptyMessage: "No se encontraron clientes con ese nombre."
    };
  }

  if (groups[0] === "direccion") {
    return {
      ok: true,
      payload: { criterio: "direccion", direccion: address },
      emptyMessage: "No se encontraron clientes con esa dirección."
    };
  }

  return {
    ok: true,
    payload: {
      criterio: "calle_altura",
      calle: street,
      altura: height || null
    },
    emptyMessage: "No se encontraron clientes con esa calle/altura."
  };
}
