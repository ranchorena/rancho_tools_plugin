// Solo sRGB hex opaco: no compone transparencias ni interpreta CSS renderizado.
function luminance(color) {
  if (typeof color !== 'string' || !/^#(?:[\da-f]{3}|[\da-f]{6})$/i.test(color)) {
    throw new TypeError('Se requiere un color hex sRGB opaco (#rgb o #rrggbb).');
  }
  const hex = color.length === 4
    ? [...color.slice(1)].map(channel => channel.repeat(2)).join('')
    : color.slice(1);
  const channels = [0, 2, 4].map(offset => {
    const channel = Number.parseInt(hex.slice(offset, offset + 2), 16) / 255;
    return channel <= 0.04045 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4;
  });
  return channels[0] * 0.2126 + channels[1] * 0.7152 + channels[2] * 0.0722;
}

export function contrastRatio(foreground, background) {
  const first = luminance(foreground);
  const second = luminance(background);
  return (Math.max(first, second) + 0.05) / (Math.min(first, second) + 0.05);
}
