import test from 'node:test';
import assert from 'node:assert/strict';
import { normalizeThemePreference, resolveTheme } from '../../src/design-system/theme.mjs';

test('normaliza preferencias ausentes y desconocidas como sistema', () => {
	assert.equal(normalizeThemePreference(undefined), 'system');
	assert.equal(normalizeThemePreference(null), 'system');
	assert.equal(normalizeThemePreference('automatic'), 'system');
	assert.equal(normalizeThemePreference(''), 'system');
});

test('conserva cada preferencia válida', () => {
	assert.equal(normalizeThemePreference('light'), 'light');
	assert.equal(normalizeThemePreference('dark'), 'dark');
	assert.equal(normalizeThemePreference('system'), 'system');
});

test('resuelve las tres preferencias con dispositivo claro y oscuro', () => {
	assert.equal(resolveTheme('light', false), 'light');
	assert.equal(resolveTheme('light', true), 'light');
	assert.equal(resolveTheme('dark', false), 'dark');
	assert.equal(resolveTheme('dark', true), 'dark');
	assert.equal(resolveTheme('system', false), 'light');
	assert.equal(resolveTheme('system', true), 'dark');
});

test('la política es pura y no depende de APIs globales del navegador', () => {
	assert.equal(resolveTheme(normalizeThemePreference('unknown'), true), 'dark');
	assert.equal(resolveTheme(normalizeThemePreference('unknown'), false), 'light');
});
