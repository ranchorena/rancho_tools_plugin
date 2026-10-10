const THEME_PREFERENCES = new Set(['light', 'dark', 'system']);

export function normalizeThemePreference(value) {
	return THEME_PREFERENCES.has(value) ? value : 'system';
}

export function resolveTheme(preference, systemIsDark) {
	const normalizedPreference = normalizeThemePreference(preference);

	if (normalizedPreference === 'system') {
		return systemIsDark ? 'dark' : 'light';
	}

	return normalizedPreference;
}
