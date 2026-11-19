const DOT_NUMBER = String.raw`([+-]?\d+(?:\.\d+)?)`;
const COMMA_NUMBER = String.raw`([+-]?\d+,\d+)`;
const DOT_PAIR = new RegExp(`^\\(?\\s*${DOT_NUMBER}\\s*(?:,|;|\\s)\\s*${DOT_NUMBER}\\s*\\)?$`);
const COMMA_PAIRS = [
  new RegExp(`^\\(?\\s*${COMMA_NUMBER}\\s*;\\s*${COMMA_NUMBER}\\s*\\)?$`),
  new RegExp(`^\\(?\\s*${COMMA_NUMBER}\\s+${COMMA_NUMBER}\\s*\\)?$`),
  new RegExp(`^\\(?\\s*${COMMA_NUMBER}\\s*,\\s*${COMMA_NUMBER}\\s*\\)?$`)
];

function coordinateResult(lat, lon) {
  const inRange = lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180;
  if (!Number.isFinite(lat) || !Number.isFinite(lon) || !inRange) {
    return { kind: "invalid_coordinates" };
  }
  return { kind: "coordinates", lat, lon };
}

export function interpretAddressQuery(text) {
  const value = String(text ?? "").trim();
  if (!value) return { kind: "empty" };

  const dotPair = value.match(DOT_PAIR);
  if (dotPair) return coordinateResult(Number(dotPair[1]), Number(dotPair[2]));

  for (const pattern of COMMA_PAIRS) {
    const match = value.match(pattern);
    if (!match) continue;
    return coordinateResult(
      Number(match[1].replace(",", ".")),
      Number(match[2].replace(",", "."))
    );
  }

  return { kind: "address", direccion: value };
}
