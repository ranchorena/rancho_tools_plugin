<script>
	export let titleId;
</script>

<div class="ds-dialog-header">
	<h2 id={titleId}><slot /></h2>
	<div class="ds-dialog-header__close"><slot name="close" /></div>
</div>

<style>
	.ds-dialog-header {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.55rem 0.9rem;
		flex-shrink: 0;
	}

	h2 {
		display: flex;
		align-items: center;
		gap: 0.45rem;
		flex: 1;
		min-width: 0;
		margin: 0;
		font-family: inherit;
		font-size: var(--ds-type-title);
		font-weight: 600;
		line-height: 1.25;
		overflow-wrap: anywhere;
	}

	.ds-dialog-header__close {
		display: flex;
		flex-shrink: 0;
		align-items: center;
	}

	.ds-dialog-header__close :global(button) {
		box-sizing: border-box;
		min-width: 2rem;
		min-height: 2rem;
		padding: 0.25rem;
		font-family: inherit;
		font-size: 1rem;
		line-height: 1.25;
	}

	@media (max-width: 768px) {
		.ds-dialog-header__close :global(button) {
			min-width: 44px;
			min-height: 44px;
		}
	}
</style>
