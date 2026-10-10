import { normalizeThemePreference, resolveTheme } from './theme.mjs';

const STORAGE_KEY = 'raweb.theme.v1';

export function createThemeController({ storage, mediaQuery, applyTheme, onPreferenceChange = () => {} }) {
	let preference = 'system';
	let started = false;
	let listening = false;

	function applyCurrentTheme() {
		applyTheme(resolveTheme(preference, mediaQuery.matches));
	}

	function handleSystemChange() {
		if (preference === 'system') applyCurrentTheme();
	}

	function start() {
		if (started) return;
		started = true;

		try {
			preference = normalizeThemePreference(storage.getItem(STORAGE_KEY));
		} catch {
			preference = 'system';
		}

		onPreferenceChange(preference);
		applyCurrentTheme();
		mediaQuery.addEventListener('change', handleSystemChange);
		listening = true;
	}

	function setPreference(value) {
		preference = normalizeThemePreference(value);
		try {
			storage.setItem(STORAGE_KEY, preference);
		} catch {
			// La elección sigue activa durante esta sesión aunque el almacenamiento esté bloqueado.
		}
		onPreferenceChange(preference);
		applyCurrentTheme();
	}

	function destroy() {
		if (listening) {
			mediaQuery.removeEventListener('change', handleSystemChange);
			listening = false;
		}
		started = false;
	}

	return { start, setPreference, destroy };
}
