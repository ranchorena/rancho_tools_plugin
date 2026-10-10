import test from 'node:test';
import assert from 'node:assert/strict';
import { createDialogFocus } from '../../src/design-system/dialog-focus.mjs';

function createControl({ visible = true, disabled = false, tabIndex = 0 } = {}) {
	return {
		isConnected: true,
		tabIndex,
		ownerDocument: { defaultView: { getComputedStyle: () => ({ visibility: visible ? 'visible' : 'hidden' }) } },
		getClientRects: () => visible ? [{}] : [],
		matches: selector => selector === ':disabled' && disabled,
		focusCount: 0,
		focus() { this.focusCount += 1; }
	};
}

function createDialog({ preferred, controls = [] } = {}) {
	let tabIndex = null;
	const attributes = new Map();
	return {
		isConnected: true,
		ownerDocument: { defaultView: { getComputedStyle: () => ({ visibility: 'visible' }) } },
		querySelector: selector => selector === '[data-dialog-initial-focus]' ? preferred ?? null : null,
		querySelectorAll: () => controls,
		hasAttribute: name => attributes.has(name),
		setAttribute(name, value) { attributes.set(name, value); if (name === 'tabindex') tabIndex = value; },
		getAttribute: name => attributes.get(name) ?? null,
		removeAttribute(name) { attributes.delete(name); if (name === 'tabindex') tabIndex = null; },
		focusCount: 0,
		focus() { this.focusCount += 1; },
		get tabIndex() { return tabIndex; }
	};
}

function afterTick() {
	return Promise.resolve();
}

test('dialogFocus gives real focus to a usable preferred control after tick', async () => {
	const preferred = createControl();
	const fallback = createControl();
	const dialog = createDialog({ preferred, controls: [fallback] });

	createDialogFocus(dialog, afterTick);
	await afterTick();

	assert.equal(preferred.focusCount, 1);
	assert.equal(fallback.focusCount, 0);
	assert.equal(dialog.focusCount, 0);
});

test('dialogFocus falls back when the preferred control is unavailable', async t => {
	for (const reason of [
		{ name: 'missing' },
		{ name: 'hidden', visible: false },
		{ name: 'disabled', disabled: true }
	]) {
		await t.test(reason.name, async () => {
			const preferred = reason.name === 'missing' ? null : createControl(reason);
			const hidden = createControl({ visible: false });
			const disabled = createControl({ disabled: true });
			const fallback = createControl();
			const dialog = createDialog({ preferred, controls: [hidden, disabled, fallback] });

			createDialogFocus(dialog, afterTick);
			await afterTick();

			assert.equal(fallback.focusCount, 1);
			assert.equal(hidden.focusCount, 0);
			assert.equal(disabled.focusCount, 0);
			assert.equal(preferred?.focusCount ?? 0, 0);
		});
	}
});

test('dialogFocus makes the dialog focusable when there is no usable control', async () => {
	const dialog = createDialog({ preferred: createControl({ visible: false }), controls: [] });
	createDialogFocus(dialog, afterTick);
	await afterTick();

	assert.equal(dialog.getAttribute('tabindex'), '-1');
	assert.equal(dialog.focusCount, 1);
});

test('dialogFocus cancels pending focus after destroy', async () => {
	let resolveTick;
	const pendingTick = new Promise(resolve => { resolveTick = resolve; });
	const target = createControl();
	const dialog = createDialog({ preferred: target, controls: [] });
	const action = createDialogFocus(dialog, () => pendingTick);

	action.destroy();
	resolveTick();
	await pendingTick;
	await Promise.resolve();

	assert.equal(target.focusCount, 0);
	assert.equal(dialog.focusCount, 0);
	assert.equal(dialog.getAttribute('tabindex'), null);
});
