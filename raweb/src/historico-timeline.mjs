/** Días civiles de la línea de pedidos históricos. No usa la zona horaria local. */

const MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
const ANCHO_ETIQUETA = 46;

export function parseFechaCivil(valor) {
  if (valor == null) return null;
  const texto = String(valor).trim().slice(0, 10);
  const coincidencia = /^(\d{4})-(\d{2})-(\d{2})$/.exec(texto);
  if (!coincidencia) return null;
  const anio = Number(coincidencia[1]);
  const mes = Number(coincidencia[2]);
  const dia = Number(coincidencia[3]);
  const utc = Date.UTC(anio, mes - 1, dia);
  const fecha = new Date(utc);
  if (fecha.getUTCFullYear() !== anio || fecha.getUTCMonth() !== mes - 1 || fecha.getUTCDate() !== dia) {
    return null;
  }
  return texto;
}

export function diaUtc(iso) {
  const [anio, mes, dia] = iso.split('-').map(Number);
  return Math.floor(Date.UTC(anio, mes - 1, dia) / 86400000);
}

export function isoDesdeDia(dia) {
  const fecha = new Date(dia * 86400000);
  const mes = String(fecha.getUTCMonth() + 1).padStart(2, '0');
  const numero = String(fecha.getUTCDate()).padStart(2, '0');
  return `${fecha.getUTCFullYear()}-${mes}-${numero}`;
}

export function agruparPedidos(pedidos) {
  const pedidosPorFecha = {};
  for (const pedido of pedidos || []) {
    const fecha = parseFechaCivil(pedido?.fecha);
    if (!fecha) continue;
    if (!pedidosPorFecha[fecha]) pedidosPorFecha[fecha] = [];
    pedidosPorFecha[fecha].push(pedido);
  }
  return { fechas: Object.keys(pedidosPorFecha).sort(), pedidosPorFecha };
}

export function sabadosDelRango(desde, hasta) {
  if (!desde || !hasta) return [];
  let dia = diaUtc(desde);
  const fin = diaUtc(hasta);
  if (fin < dia) return [];
  const weekday = new Date(dia * 86400000).getUTCDay();
  dia += (6 - weekday + 7) % 7;
  const sabados = [];
  while (dia <= fin) {
    sabados.push(isoDesdeDia(dia));
    dia += 7;
  }
  return sabados;
}

export function posicionFecha(fecha, fechas) {
  if (!fechas?.length) return 0;
  if (fechas.length === 1) return 0.5;
  const indice = fechas.indexOf(fecha);
  if (indice < 0) return 0;
  return indice / (fechas.length - 1);
}

export function fechaDesdePosicion(ratio, fechas) {
  if (!fechas?.length) return null;
  const acotado = Math.min(1, Math.max(0, Number(ratio) || 0));
  const indice = Math.round(acotado * (fechas.length - 1));
  return fechas[indice];
}

export function acercarFecha(fecha, fechas) {
  if (!fechas?.length) return null;
  if (!fecha) return fechas[fechas.length - 1];
  const objetivo = diaUtc(fecha);
  let mejor = fechas[0];
  let mejorDistancia = Math.abs(diaUtc(fechas[0]) - objetivo);
  for (let i = 1; i < fechas.length; i += 1) {
    const candidata = fechas[i];
    const distancia = Math.abs(diaUtc(candidata) - objetivo);
    if (distancia < mejorDistancia || (distancia === mejorDistancia && diaUtc(candidata) > diaUtc(mejor))) {
      mejor = candidata;
      mejorDistancia = distancia;
    }
  }
  return mejor;
}

export function fechaAnterior(fecha, fechas) {
  const indice = fechas.indexOf(fecha);
  if (indice <= 0) return null;
  return fechas[indice - 1];
}

export function fechaSiguiente(fecha, fechas) {
  const indice = fechas.indexOf(fecha);
  if (indice < 0 || indice >= fechas.length - 1) return null;
  return fechas[indice + 1];
}

export function textoFecha(iso) {
  const fecha = parseFechaCivil(iso);
  if (!fecha) return '';
  const [, mes, dia] = fecha.split('-');
  return `${Number(dia)} ${MESES[Number(mes) - 1]} ${fecha.slice(0, 4)}`;
}

export function textoDiaMesAnio(iso) {
  const fecha = parseFechaCivil(iso);
  if (!fecha) return '';
  const [anio, mes, dia] = fecha.split('-');
  return `${dia}/${mes}/${anio}`;
}

export function parseFechaEditable(valor) {
  if (valor == null) return null;
  const texto = String(valor).trim().toLowerCase().replace(/\s+/g, ' ');
  if (!texto) return null;
  const iso = parseFechaCivil(texto);
  if (iso && texto.startsWith(iso)) return iso;
  const numerica = /^(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})$/.exec(texto);
  if (numerica) {
    return parseFechaCivil(`${numerica[3]}-${numerica[2].padStart(2, '0')}-${numerica[1].padStart(2, '0')}`);
  }
  const escrita = /^(\d{1,2})\s+([a-z]+)\.?\s+(\d{4})$/.exec(
    texto.normalize('NFD').replace(/[\u0300-\u036f]/g, '')
  );
  if (!escrita) return null;
  const mes = MESES.indexOf(escrita[2].slice(0, 3)) + 1;
  if (mes < 1) return null;
  return parseFechaCivil(`${escrita[3]}-${String(mes).padStart(2, '0')}-${escrita[1].padStart(2, '0')}`);
}

export function etiquetaEscala(iso) {
  const fecha = parseFechaCivil(iso);
  if (!fecha) return { anio: '', dia: '' };
  return { anio: fecha.slice(0, 4), dia: fecha.slice(5).replace('-', '/') };
}

export function etiquetasVisibles(fechas, anchoPx, anchoEtiquetaPx = ANCHO_ETIQUETA) {
  const total = fechas?.length || 0;
  if (!total) return [];
  if (!anchoPx || anchoPx <= 0) return fechas.map(() => false);
  const mitad = anchoEtiquetaPx / 2;
  const visibles = [];
  let ultimo = -Infinity;
  for (let indice = 0; indice < fechas.length; indice += 1) {
    const x = posicionFecha(fechas[indice], fechas) * anchoPx;
    const mostrar = x >= mitad && x <= anchoPx - mitad && x - ultimo >= anchoEtiquetaPx;
    visibles.push(mostrar);
    if (mostrar) ultimo = x;
  }
  if (!visibles.some(Boolean) && anchoPx >= anchoEtiquetaPx) {
    visibles[Math.floor((fechas.length - 1) / 2)] = true;
  }
  return visibles;
}
