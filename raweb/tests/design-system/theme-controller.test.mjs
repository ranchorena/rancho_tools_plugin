import test from 'node:test';
import assert from 'node:assert/strict';
import { createThemeController } from '../../src/design-system/theme-controller.mjs';

function createStorage(initialValue) {
	let value = initialValue;
	const calls = [];

	return {
		calls,
		getItem(key) {
			calls.push(['getItem', key]);
			return value;
		},
		setItem(key, nextValue) {
			calls.push(['setItem', key, nextValue]);
			value = nextValue;
		},
		get value() {
			return value;
		}
	};
}

function createMediaQuery(matches = false) {
	const listeners = new Set();
	return {
		matches,
		addEventListener(type, listener) {
			assert.equal(type, 'change');
			listeners.add(listener);
		},
		removeEventListener(type, listener) {
			assert.equal(type, 'change');
			listeners.delete(listener);
		},
		emit(nextMatches) {
			this.matches = nextMatches;
			for (const listener of listeners) listener({ matches: nextMatches });
		},
		get listenerCount() {
			return listeners.size;
		}
	};
}

test('lee la preferencia guardada y aplica el tema resuelto al iniciar', () => {
	const storage = createStorage('dark');
	const mediaQuery = createMediaQuery(false);
	const applied = [];
	const preferences = [];
	const controller = createThemeController({
		storage,
		mediaQuery,
		applyTheme: (theme) => applied.push(theme),
		onPreferenceChange: (preference) => preferences.push(preference)
	});

	controller.start();

	assert.deepEqual(applied, ['dark']);
	assert.deepEqual(preferences, ['dark']);
	assert.equal(storage.calls[0][0], 'getItem');
	assert.equal(storage.calls[0][1], 'raweb.theme.v1');
});

test('guarda la elección manual y un fallo de escritura no impide aplicarla', () => {
	const storage = createStorage(null);
	const mediaQuery = createMediaQuery(false);
	const applied = [];
	const preferences = [];
	const controller = createThemeController({
		storage: {
			getItem: storage.getItem.bind(storage),
			setItem() {
				throw new Error('storage denied');
			}
		},
		mediaQuery,
		applyTheme: (theme) => applied.push(theme),
		onPreferenceChange: (preference) => preferences.push(preference)
	});

	controller.start();
	controller.setPreference('dark');

	assert.deepEqual(applied, ['light', 'dark']);
	assert.deepEqual(preferences, ['system', 'dark']);
});

test('persiste la elección normalizada y tolera un rechazo al leer almacenamiento', () => {
	const storage = createStorage(null);
	const mediaQuery = createMediaQuery(true);
	const applied = [];
	const controller = createThemeController({
		storage,
		mediaQuery,
		applyTheme: (theme) => applied.push(theme)
	});

	controller.start();
	controller.setPreference('light');

	assert.equal(storage.value, 'light');
	assert.deepEqual(storage.calls.at(-1), ['setItem', 'raweb.theme.v1', 'light']);

	const rejectedRead = createThemeController({
		storage: { getItem() { throw new Error('storage denied'); }, setItem() {} },
		mediaQuery,
		applyTheme: (theme) => applied.push(theme)
	});
	rejectedRead.start();
	assert.deepEqual(applied, ['dark', 'light', 'dark']);
});

test('Sistema sigue los cambios del dispositivo y destruye la suscripción', () => {
	const storage = createStorage(null);
	const mediaQuery = createMediaQuery(false);
	const applied = [];
	const controller = createThemeController({
		storage,
		mediaQuery,
		applyTheme: (theme) => applied.push(theme)
	});

	controller.start();
	mediaQuery.emit(true);
	mediaQuery.emit(false);
	controller.destroy();

	assert.deepEqual(applied, ['light', 'dark', 'light']);
	assert.equal(mediaQuery.listenerCount, 0);
});

test('un cambio del dispositivo no sobreescribe una elección explícita', () => {
	const storage = createStorage('dark');
	const mediaQuery = createMediaQuery(false);
	const applied = [];
	const controller = createThemeController({
		storage,
		mediaQuery,
		applyTheme: (theme) => applied.push(theme)
	});

	controller.start();
	mediaQuery.emit(true);

	assert.deepEqual(applied, ['dark']);
	assert.equal(storage.value, 'dark');
	assert.equal(storage.calls.filter(([method]) => method === 'setItem').length, 0);
});
