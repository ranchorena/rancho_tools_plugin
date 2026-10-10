import test from 'node:test';
import assert from 'node:assert/strict';
import { catalog, nativeAlerts } from '../../src/design-system/catalog.mjs';

const requiredFamilies = [
  'C-BUTTON', 'C-FIELD', 'C-CHOICE', 'C-THEME', 'C-DIALOG', 'C-NAV',
  'C-TABLE', 'C-STATS', 'C-NOTICE', 'C-PANEL', 'C-FLOAT', 'C-INFO'
];
const validExperienceIds = new Set(['X-NAV', 'X-DIR', 'X-CLI', 'X-ADD', 'X-PED', 'X-NOT', 'X-MAP']);
const validRequirementIds = new Set(Array.from({ length: 24 }, (_, index) => `RF-${index + 1}`));
const validStateIds = new Set([
  'normal', 'hover', 'active', 'focus', 'selected', 'disabled', 'loading', 'message',
  'open', 'closed', 'checked', 'unchecked', 'visible', 'hidden', 'error', 'success', 'scroll'
]);

test('cataloga todas las familias de coverage con IDs únicos y trazabilidad RF válida', () => {
  assert.deepEqual(catalog.map(({ id }) => id), requiredFamilies);
  assert.equal(new Set(catalog.map(({ id }) => id)).size, catalog.length);

  for (const item of catalog) {
    assert.ok(item.name, `${item.id} requiere nombre`);
    assert.ok(item.variants.length > 0, `${item.id} requiere variantes existentes/aprobadas`);
    assert.equal(new Set(item.variants).size, item.variants.length, `${item.id}: variante duplicada`);
    assert.ok(item.requirements.length > 0, `${item.id} requiere RF`);
    assert.ok(item.experiences.length > 0, `${item.id} requiere experiencia`);
    for (const experience of item.experiences) {
      assert.ok(validExperienceIds.has(experience), `${item.id}: experiencia desconocida ${experience}`);
    }
    for (const requirement of item.requirements) {
      assert.ok(validRequirementIds.has(requirement), `${item.id}: RF desconocido ${requirement}`);
    }
  }
});

test('declara estados aplicables y no aplicables sin duplicarlos ni introducir estados nuevos', () => {
  for (const item of catalog) {
    assert.ok(Array.isArray(item.states.applicable), `${item.id}: falta aplicables`);
    assert.ok(Array.isArray(item.states.notApplicable), `${item.id}: falta no aplicables`);
    assert.ok(item.states.applicable.length + item.states.notApplicable.length > 0, item.id);

    const applicable = item.states.applicable.map(({ id }) => id);
    const notApplicable = item.states.notApplicable.map(({ id }) => id);
    assert.equal(new Set([...applicable, ...notApplicable]).size, applicable.length + notApplicable.length,
      `${item.id}: estado duplicado o clasificado en ambas listas`);

    for (const state of [...item.states.applicable, ...item.states.notApplicable]) {
      assert.ok(validStateIds.has(state.id), `${item.id}: estado no inventariado ${state.id}`);
      assert.ok(state.source, `${item.id}/${state.id}: falta procedencia`);
      if (item.states.notApplicable.includes(state)) assert.ok(state.reason, `${item.id}/${state.id}: falta motivo`);
    }
  }
});

test('alertas nativas se excluyen de apariencia y contraste, pero su funcionamiento se verifica', () => {
  assert.deepEqual(nativeAlerts.map(({ id }) => id), ['A-01', 'A-02', 'A-03']);
  assert.equal(new Set(nativeAlerts.map(({ id }) => id)).size, nativeAlerts.length);

  for (const alert of nativeAlerts) {
    assert.ok(alert.trigger);
    assert.ok(alert.message);
    assert.equal(alert.presentation, 'native-browser-excluded');
    assert.equal(alert.behavior, 'verify-trigger-message-function');
    assert.ok(alert.requirements.includes('RF-23'));
  }
});
