import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { contrastRatio } from './support/contrast.mjs';

// Pares declarados opacos; no representan cascada, composición ni render.
const textPairs = [
  ['text', 'surface'], ['text', 'background'],
  ['text-muted', 'surface'], ['text-muted', 'background'],
  ...['primary', 'secondary', 'location'].flatMap(variant =>
    ['', '-hover', '-active'].map(state => [`on-${variant}`, `${variant}${state}`])),
  ['on-selected', 'selected'], ['success', 'success-surface'],
  ['warning', 'warning-surface'], ['error', 'error-surface'],
  ['on-disabled', 'disabled']
];
const controlPairs = ['surface', 'background'].flatMap(background =>
  ['border', 'focus', 'primary', 'primary-hover', 'primary-active',
    'location', 'location-hover', 'location-active'].map(foreground => [foreground, background]));

test('negro/blanco da 21:1, simétrico, y colores iguales dan 1:1', () => {
  assert.equal(contrastRatio('#000000', '#ffffff'), 21);
  assert.equal(contrastRatio('#fff', '#000'), 21);
  for (const color of ['#000', '#fff', '#2563eb', '#93C5FD']) {
    assert.equal(contrastRatio(color, color), 1);
  }
  assert.equal(contrastRatio('#2563eb', '#f8f9fa'), contrastRatio('#f8f9fa', '#2563eb'));
});

test('umbrales 4,5 y 3 se comparan sin redondear', () => {
  assert.ok(contrastRatio('#767676', '#ffffff') >= 4.5);
  const belowNormal = contrastRatio('#777777', '#ffffff');
  assert.ok(Math.abs(belowNormal - 4.478089453577214) < 1e-12);
  assert.ok(belowNormal < 4.5);
  assert.equal(Number(belowNormal.toFixed(1)), 4.5);
  assert.ok(contrastRatio('#949494', '#ffffff') >= 3);
  const belowLarge = contrastRatio('#959595', '#ffffff');
  assert.ok(belowLarge < 3);
  assert.equal(Number(belowLarge.toFixed(1)), 3);
});

test('rechaza transparencias y formatos ajenos al contrato hex opaco', () => {
  for (const color of ['#fff8', '#ffffff80', 'transparent', 'rgba(0,0,0,.5)', '#ggg', '#12345', null]) {
    assert.throws(() => contrastRatio(color, '#fff'), TypeError);
    assert.throws(() => contrastRatio('#fff', color), TypeError);
  }
});

const css = await readFile(new URL('../../public/design-system.css', import.meta.url), 'utf8');
for (const theme of ['light', 'dark']) {
  test(`pares opacos de paleta ${theme}: texto ≥4,5 y controles/estados ≥3`, context => {
    const block = css.match(new RegExp(`:root\\[data-theme="${theme}"\\]\\s*\\{([^}]+)\\}`));
    assert.ok(block, `Falta bloque de tema ${theme}`);
    const palette = Object.fromEntries([...block[1].matchAll(/--ds-([\w-]+)\s*:\s*(#[\da-f]{6})\s*;/gi)]
      .map(([, name, value]) => [name, value]));
    assert.equal(Object.keys(palette).length, 28, 'Inventario de colores de T9');
    for (const [pairs, threshold] of [[textPairs, 4.5], [controlPairs, 3]]) {
      for (const [foreground, background] of pairs) {
        assert.ok(palette[foreground], `Falta ${foreground}`);
        assert.ok(palette[background], `Falta ${background}`);
        const ratio = contrastRatio(palette[foreground], palette[background]);
        assert.ok(ratio >= threshold, `${theme}: ${foreground}/${background} = ${ratio} < ${threshold}`);
        context.diagnostic(`${foreground}/${background}: ${ratio} ≥ ${threshold}`);
      }
    }
  });
}
