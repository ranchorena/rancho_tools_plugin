import { tick } from 'svelte';

export function dialogFocus(node) {
	return createDialogFocus(node);
}

export function createDialogFocus(node, nextTick = tick) {
	let destroyed = false;
	let addedTabIndex = false;

	nextTick().then(() => {
		if (destroyed || !node.isConnected) return;

		const isUsable = control => {
			if (!control || control.matches(':disabled') || control.tabIndex < 0) return false;
			const style = control.ownerDocument.defaultView.getComputedStyle(control);
			return control.getClientRects().length > 0 && style.visibility === 'visible';
		};
		const preferred = node.querySelector('[data-dialog-initial-focus]');
		if (isUsable(preferred)) {
			preferred.focus();
			return;
		}

		const controls = node.querySelectorAll(
			'button, input, select, textarea, a[href], [tabindex], [contenteditable="true"]'
		);
		const target = Array.from(controls).find(isUsable);

		if (target) {
			target.focus();
		} else {
			if (!node.hasAttribute('tabindex')) {
				node.setAttribute('tabindex', '-1');
				addedTabIndex = true;
			}
			node.focus();
		}
	});

	return {
		destroy() {
			destroyed = true;
			if (addedTabIndex && node.getAttribute('tabindex') === '-1') {
				node.removeAttribute('tabindex');
			}
			// El padre distingue cierre final de selección de ubicación y gestiona el retorno.
		}
	};
}
