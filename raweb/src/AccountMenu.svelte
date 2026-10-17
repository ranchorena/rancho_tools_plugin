<script>
  import { createEventDispatcher } from 'svelte';
  import ThemeSelector from './design-system/ThemeSelector.svelte';
  import UiIcon from './design-system/Icon.svelte';

  export let username = '';
  export let themePreference = 'system';

  const dispatch = createEventDispatcher();

  let menuAbierto = false;
  let menuCuenta;

  function alternarMenu() {
    menuAbierto = !menuAbierto;
  }

  function cerrarSiCorresponde(event) {
    if (!menuAbierto) return;
    const target = event.target;
    if (menuCuenta?.contains(target)) return;
    if (target instanceof Element && target.closest('#account-menu-panel')) return;
    menuAbierto = false;
  }

  function cerrarConEscape(event) {
    if (event.key === 'Escape' && menuAbierto) {
      menuAbierto = false;
    }
  }

  function cambiarTema(event) {
    dispatch('themechange', event.detail);
  }

  function cerrarSesion() {
    menuAbierto = false;
    dispatch('logout');
  }

  function portal(node) {
    document.body.appendChild(node);
    return {
      destroy() {
        node.remove();
      }
    };
  }

  function anclarPanel(node) {
    const colocar = () => {
      const disparador = menuCuenta?.querySelector('.account-trigger');
      if (!disparador) return;
      const rect = disparador.getBoundingClientRect();
      node.style.top = `${Math.round(rect.bottom + 6)}px`;
    };
    colocar();
    window.addEventListener('resize', colocar);
    return {
      destroy() {
        window.removeEventListener('resize', colocar);
      }
    };
  }
</script>

<svelte:window on:pointerdown|capture={cerrarSiCorresponde} on:keydown={cerrarConEscape} />

<div class="account-menu" bind:this={menuCuenta}>
  <button
    type="button"
    class="account-trigger"
    class:is-open={menuAbierto}
    aria-haspopup="true"
    aria-expanded={menuAbierto}
    aria-controls="account-menu-panel"
    aria-label={username ? `Menú de cuenta de ${username}` : 'Menú de cuenta'}
    on:click={alternarMenu}
  >
    <span class="account-name">{username || 'Cuenta'}</span>
    <span class="account-chevron" class:is-open={menuAbierto} aria-hidden="true"></span>
    <span class="account-avatar" aria-hidden="true">
      <UiIcon name="user" size={16} />
    </span>
  </button>

  {#if menuAbierto}
    <div id="account-menu-panel" class="account-panel" use:portal use:anclarPanel>
      <div class="account-theme">
        <ThemeSelector id="theme-account" value={themePreference} on:change={cambiarTema} />
      </div>
      <hr class="account-separator" />
      <button type="button" class="account-item" disabled title="Todavía no está disponible">
        <UiIcon name="lock" size={16} />
        <span>Cambiar contraseña</span>
      </button>
      <button type="button" class="account-item" on:click={cerrarSesion}>
        <UiIcon name="logout" size={16} />
        <span>Cerrar sesión</span>
      </button>
    </div>
  {/if}
</div>

<style>
  .account-menu {
    position: relative;
  }

  button.account-trigger {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    margin: 0;
    padding: 0.15rem 0.2rem 0.15rem 0.55rem;
    min-height: 2.125rem;
    border: 1px solid transparent;
    border-radius: 999px;
    background-color: transparent;
    color: var(--ds-text);
    font-size: var(--ds-type-nav);
    font-weight: 600;
    line-height: 1.2;
    white-space: nowrap;
  }

  button.account-trigger:hover:not(:disabled),
  button.account-trigger.is-open {
    background-color: var(--ds-secondary-hover);
    border-color: transparent;
  }

  .account-name {
    max-width: 9rem;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .account-chevron {
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid currentColor;
    opacity: 0.75;
  }

  .account-chevron.is-open {
    transform: rotate(180deg);
  }

  .account-avatar {
    display: grid;
    place-items: center;
    width: 1.85rem;
    height: 1.85rem;
    border-radius: 50%;
    background: var(--ds-primary);
    color: var(--ds-on-primary);
  }

  .account-panel {
    position: fixed;
    right: 0.5rem;
    z-index: 1001;
    min-width: 15rem;
    padding: 0.35rem;
    background: var(--ds-surface);
    color: var(--ds-text);
    border: 1px solid var(--ds-divider);
    border-radius: var(--ds-radius-medium);
    box-shadow: var(--ds-shadow-panel);
  }

  .account-theme :global(.theme-selector) {
    width: 100%;
    justify-content: space-between;
    padding: 0.4rem 0.65rem;
  }

  .account-panel :global(select) {
    width: auto;
    min-height: 2rem;
    margin: 0;
    padding: 0.2rem 0.45rem;
    font-size: var(--ds-type-label);
  }

  .account-separator {
    height: 1px;
    margin: 0.25rem 0.35rem;
    border: 0;
    background: var(--ds-divider);
  }

  button.account-item {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    width: 100%;
    margin: 0;
    padding: 0.55rem 0.65rem;
    min-height: 2.25rem;
    border: 1px solid transparent;
    border-radius: var(--ds-radius-small);
    background-color: transparent;
    color: var(--ds-text);
    font-size: var(--ds-type-body);
    font-weight: 500;
    line-height: 1.2;
    text-align: left;
    white-space: nowrap;
  }

  button.account-item:hover:not(:disabled) {
    background-color: var(--ds-secondary-hover);
    border-color: transparent;
  }

  button.account-item:disabled {
    color: var(--ds-text-muted);
    background-color: transparent;
    border-color: transparent;
    opacity: 0.72;
    cursor: not-allowed;
  }

  @media (max-width: 768px) {
    button.account-trigger,
    button.account-item {
      margin-bottom: 0;
      font-size: 0.875rem;
    }

    button.account-trigger {
      padding: 0.1rem 0.15rem 0.1rem 0.45rem;
      min-height: 2.25rem;
    }

    .account-name {
      max-width: 6.5rem;
    }
  }
</style>
