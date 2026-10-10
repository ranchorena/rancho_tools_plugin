import test from 'node:test';
import assert from 'node:assert/strict';
import { chooseFocusReturn } from '../../src/design-system/focus-policy.mjs';

test('el disparador presente y visible tiene prioridad en ambos orígenes', () => {
	for (const openedFromMobileMenu of [false, true]) {
		assert.equal(chooseFocusReturn({
			triggerPresent: true, triggerVisible: true, openedFromMobileMenu,
			menuButtonPresent: true, menuButtonVisible: true
		}), 'trigger');
	}
});

test('una acción móvil oculta o desmontada retorna a Menú visible', () => {
	for (const [triggerPresent, triggerVisible] of [[true, false], [false, false], [false, true]]) {
		assert.equal(chooseFocusReturn({
			triggerPresent, triggerVisible, openedFromMobileMenu: true,
			menuButtonPresent: true, menuButtonVisible: true
		}), 'menu');
	}
});

test('el origen escritorio no utiliza Menú como destino alternativo', () => {
	for (const [triggerPresent, triggerVisible] of [[true, false], [false, false], [false, true]]) {
		assert.equal(chooseFocusReturn({
			triggerPresent, triggerVisible, openedFromMobileMenu: false,
			menuButtonPresent: true, menuButtonVisible: true
		}), null);
	}
});

test('Menú ausente u oculto no es destino para una acción móvil desaparecida', () => {
	for (const [triggerPresent, triggerVisible] of [[true, false], [false, false]]) {
		for (const [menuButtonPresent, menuButtonVisible] of [[true, false], [false, false], [false, true]]) {
			assert.equal(chooseFocusReturn({
				triggerPresent, triggerVisible, openedFromMobileMenu: true,
				menuButtonPresent, menuButtonVisible
			}), null);
		}
	}
});

test('la decisión solo devuelve un destino y no modifica los hechos recibidos', () => {
	const facts = Object.freeze({
		triggerPresent: false, triggerVisible: false, openedFromMobileMenu: true,
		menuButtonPresent: true, menuButtonVisible: true
	});
	assert.equal(chooseFocusReturn(facts), 'menu');
	assert.equal(chooseFocusReturn(facts), 'menu');
	assert.deepEqual(facts, {
		triggerPresent: false, triggerVisible: false, openedFromMobileMenu: true,
		menuButtonPresent: true, menuButtonVisible: true
	});
});
