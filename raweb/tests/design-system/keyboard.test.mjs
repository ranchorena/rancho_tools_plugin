import test from 'node:test';
import assert from 'node:assert/strict';
import { shouldActivateRow } from '../../src/design-system/keyboard.mjs';

test('Enter y Espacio activan una pulsación en la propia fila', () => {
	assert.equal(shouldActivateRow('Enter', false, true), true);
	assert.equal(shouldActivateRow(' ', false, true), true);
});

test('otras teclas no activan la fila', () => {
	for (const key of ['Tab', 'Escape', 'ArrowDown', 'a', '', 'Space', 'Spacebar']) {
		assert.equal(shouldActivateRow(key, false, true), false, key);
	}
});

test('no se repite la activación al mantener Enter o Espacio', () => {
	for (const key of ['Enter', ' ']) {
		assert.equal(shouldActivateRow(key, true, true), false);
	}
});

test('Enter y Espacio en descendientes no activan la fila ni siquiera sin repeat', () => {
	for (const key of ['Enter', ' ']) {
		for (const isRepeat of [false, true]) {
			assert.equal(shouldActivateRow(key, isRepeat, false), false);
		}
	}
});
