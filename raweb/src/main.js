import Catalog from './design-system/Catalog.svelte';
import App from './App.svelte';

const isCatalogMode = new URLSearchParams(window.location.search).get('catalog') === 'design-system';

let app;

if (isCatalogMode) {
	app = new Catalog({ target: document.body });
} else {
	app = new App({ target: document.body });
}

export default app;
