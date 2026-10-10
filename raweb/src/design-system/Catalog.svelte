<script>
	import { catalog, nativeAlerts } from './catalog.mjs';

	const variantCount = catalog.reduce((total, family) => total + family.variants.length, 0);
	const stateCount = catalog.reduce((total, family) => total + family.states.applicable.length, 0);
	const foundations = [
		{ id: 'color', title: 'Color y significado', purpose: 'Azul para acciones principales y navegación; verde para seleccionar ubicación. Los tonos semánticos distinguen selección, éxito, advertencia y error.', examples: [
			{ token: '--ds-primary', label: 'Acción principal', value: 'var(--ds-primary)' },
			{ token: '--ds-location', label: 'Ubicación', value: 'var(--ds-location)' },
			{ token: '--ds-selected', label: 'Selección', value: 'var(--ds-selected)' },
			{ token: '--ds-success', label: 'Éxito', value: 'var(--ds-success)' },
			{ token: '--ds-warning', label: 'Advertencia', value: 'var(--ds-warning)' },
			{ token: '--ds-error', label: 'Error', value: 'var(--ds-error)' }
		] },
		{ id: 'type', title: 'Tipografía', purpose: 'Familia de sistema para texto de interfaz y Courier New para coordenadas; jerarquía por tamaño y peso.', samples: [
			{ token: '--ds-text-small', label: 'Secundaria', value: '0.875rem' },
			{ token: '--ds-text-base', label: 'Base', value: '1rem' },
			{ token: '--ds-text-large', label: 'Título', value: '1.5rem' }
		] },
		{ id: 'space', title: 'Espaciado y dimensiones', purpose: 'Escala de separación en rem; dimensiones de controles existentes se mantienen particulares al componente.', samples: [
			{ token: '--ds-space-1', label: '1', value: '0.25rem' }, { token: '--ds-space-2', label: '2', value: '0.5rem' },
			{ token: '--ds-space-3', label: '3', value: '0.75rem' }, { token: '--ds-space-4', label: '4', value: '1rem' },
			{ token: '--ds-space-6', label: '6', value: '1.5rem' }, { token: '--ds-space-8', label: '8', value: '2rem' }
		] },
		{ id: 'edges', title: 'Bordes, radios y elevación', purpose: 'Bordes neutros y radios discretos para superficies; sombras separan paneles y diálogos del fondo.', samples: [
			{ token: '--ds-border-width', label: 'Borde', value: '1px' }, { token: '--ds-border-strong', label: 'Borde destacado', value: '2px' },
			{ token: '--ds-radius-small', label: 'Radio pequeño', value: '6px' }, { token: '--ds-radius-medium', label: 'Radio medio', value: '8px' },
			{ token: '--ds-radius-large', label: 'Radio grande', value: '12px' }, { token: '--ds-radius-round', label: 'Circular', value: '50%' },
			{ token: '--ds-shadow-panel', label: 'Panel', value: '0 4px 12px rgb(0 0 0 / 15%)' },
			{ token: '--ds-shadow-dialog', label: 'Diálogo', value: '0 20px 25px -5px rgb(0 0 0 / 20%)' }
		] }
	];
</script>

<svelte:head>
	<title>Catálogo del design system — RAWEB</title>
</svelte:head>

<main class="catalog-shell" data-design-system-catalog>
	<header class="catalog-header">
		<p class="catalog-eyebrow">RAWEB · Design system</p>
		<h1>Catálogo de componentes</h1>
		<p>Inventario aprobado de elementos y estados existentes de la interfaz.</p>
	</header>

	<section aria-labelledby="catalog-summary-title">
		<h2 id="catalog-summary-title">Inventario</h2>
		<p>{catalog.length} familias · {variantCount} variantes · {stateCount} estados aplicables · {nativeAlerts.length} alertas nativas</p>
		<ul class="family-list">
			{#each catalog as family (family.id)}
				<li class="family-card ds-surface">
					<div>
						<h3>{family.name}</h3>
						<p class="family-id">{family.id}</p>
					</div>
					<p>{family.variants.length} variantes · {family.states.applicable.length} estados aplicables · {family.states.notApplicable.length} no aplicables</p>
				</li>
			{/each}
		</ul>
	</section>

	<section class="foundations" aria-labelledby="foundations-title">
		<h2 id="foundations-title">Fundaciones visuales</h2>
		<p>Valores de la hoja compartida <code>design-system.css</code>. Los ejemplos son ilustrativos: no representan un nuevo estado del producto.</p>
		{#each foundations as foundation (foundation.id)}
			<article class="foundation-card ds-surface" aria-labelledby="foundation-{foundation.id}">
				<h3 id="foundation-{foundation.id}">{foundation.title}</h3>
				<p>{foundation.purpose}</p>
				{#if foundation.examples}
					<ul class="swatches">
						{#each foundation.examples as example (example.token)}
							<li class="swatch-item"><span class="swatch" style="background-color: {example.value}" aria-hidden="true"></span><span><strong>{example.label}</strong><code>{example.token}</code></span></li>
						{/each}
					</ul>
				{:else}
					<ul class="sample-list">
						{#each foundation.samples as sample (sample.token)}
							<li><span class="sample-mark" style="--sample-size: {sample.value}"></span><span><strong>{sample.label}</strong><code>{sample.token}</code><small>{sample.value}</small></span></li>
						{/each}
					</ul>
				{/if}
			</article>
		{/each}

		<article class="foundation-card ds-surface" aria-labelledby="foundation-icon">
			<h3 id="foundation-icon">Iconografía</h3>
			<p>Se conservan los símbolos y emojis existentes junto con texto o nombre accesible; no se modifica la simbología cartográfica.</p>
			<ul class="icon-samples"><li><span aria-hidden="true">🔎</span> Búsqueda</li><li><span aria-hidden="true">📍</span> Ubicación</li><li><span aria-hidden="true">☰</span> Menú</li><li><span aria-hidden="true">×</span> Cierre</li></ul>
		</article>
	</section>

	<section class="identity ds-surface" aria-labelledby="identity-title">
		<h2 id="identity-title">Identidad actual y reglas compartidas</h2>
		<p>La comparación describe rasgos registrados en el inventario; los valores nuevos de la hoja compartida se muestran arriba. No se agregan categorías ni colores.</p>
		<div class="comparison">
			<div><h3>Identidad observada</h3><ul><li>Acciones y navegación azules; ubicación verde.</li><li>Tipografía de sistema, con Arial declarada localmente en App e indicador de coordenadas en Courier New.</li><li>Espaciado y dimensiones definidos por cada experiencia, con separaciones frecuentes de 0.25–2rem.</li><li>Bordes neutros, radios de 6/8/12px y sombras locales.</li><li>Iconos mediante emojis, caracteres y controles DOM de OpenLayers.</li></ul></div>
			<div><h3>Fundaciones documentadas</h3><ul><li>Azul semántico para acción principal y verde para ubicación; se mantienen distintos del éxito.</li><li>Escalas compartidas de tipografía y espacio, respetando dimensiones particulares existentes.</li><li>Tokens explícitos para bordes, radios y sombras de panel/diálogo.</li><li>Se conservan símbolos actuales con texto o nombre accesible.</li></ul></div>
		</div>
		<p class="limitation">Limitación: la identidad previa reúne valores locales distintos; el inventario no establece un único valor efectivo de color, espaciado o sombra para toda la UI. Esta comparación no los infiere ni los homogeneiza.</p>
	</section>
</main>

<style>
	:global(body) {
		margin: 0;
		background: var(--ds-background);
		color: var(--ds-text);
	}

	.catalog-shell {
		box-sizing: border-box;
		width: min(100% - 2rem, 960px);
		margin: 0 auto;
		padding: 2rem 0 4rem;
	}

	.catalog-header {
		margin-bottom: 2rem;
		padding: 1.5rem;
		border-radius: 12px;
		background: var(--ds-surface);
		color: var(--ds-text);
		box-shadow: 0 2px 8px rgb(0 0 0 / 10%);
	}

	.catalog-eyebrow,
	.family-id {
		color: var(--ds-text-muted);
		font-size: 0.875rem;
	}

	h1,
	h2,
	h3,
	p {
		margin-top: 0;
	}

	h1 { margin-bottom: 0.5rem; }

	.family-list {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(min(100%, 280px), 1fr));
		gap: 1rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}

	.family-card {
		padding: 1rem;
		border: 1px solid var(--ds-border);
		border-radius: 8px;
	}

	.family-card h3 { margin-bottom: 0.25rem; }
	.family-card p:last-child { margin-bottom: 0; color: var(--ds-text-muted); }

	.foundations, .identity { margin-top: 2rem; }
	.foundations > p, .identity > p { color: var(--ds-text-muted); }
	.foundation-card, .identity { margin-top: 1rem; padding: 1.25rem; border: 1px solid var(--ds-border); border-radius: 8px; }
	.foundation-card h3, .comparison h3 { margin-bottom: 0.5rem; }
	.foundation-card > p { color: var(--ds-text-muted); }
	.swatches, .sample-list, .icon-samples { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 210px), 1fr)); gap: 0.75rem; margin: 1rem 0 0; padding: 0; list-style: none; }
	.swatch-item, .sample-list li, .icon-samples li { display: flex; align-items: center; gap: 0.75rem; min-width: 0; }
	.swatch { flex: 0 0 2.5rem; width: 2.5rem; height: 2.5rem; border: 1px solid var(--ds-border); border-radius: 6px; }
	.swatch-item > span:last-child, .sample-list li > span:last-child { display: grid; gap: 0.1rem; }
	code, .sample-list small { color: var(--ds-text-muted); font-size: 0.8rem; overflow-wrap: anywhere; }
	.sample-mark { display: block; flex: 0 0 var(--sample-size); width: var(--sample-size); height: var(--sample-size); max-width: 100%; background: var(--ds-primary); border-radius: 2px; }
	.icon-samples span { font-size: 1.25rem; }
	.comparison { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1.5rem; }
	.comparison ul { margin: 0; padding-left: 1.25rem; }
	.comparison li + li { margin-top: 0.5rem; }
	.limitation { margin: 1.25rem 0 0; padding-top: 1rem; border-top: 1px solid var(--ds-border); }
	@media (max-width: 600px) { .comparison { grid-template-columns: 1fr; gap: 1rem; } .foundation-card, .identity { padding: 1rem; } }

	@media (max-width: 600px) {
		.catalog-shell { width: min(100% - 1.5rem, 960px); padding-top: 1rem; }
		.catalog-header { padding: 1rem; }
	}
</style>
