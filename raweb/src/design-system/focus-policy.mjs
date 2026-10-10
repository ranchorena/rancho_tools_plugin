export function chooseFocusReturn({
	triggerPresent,
	triggerVisible,
	openedFromMobileMenu,
	menuButtonPresent,
	menuButtonVisible
}) {
	if (triggerPresent && triggerVisible) {
		return 'trigger';
	}

	if (openedFromMobileMenu && menuButtonPresent && menuButtonVisible) {
		return 'menu';
	}

	return null;
}
